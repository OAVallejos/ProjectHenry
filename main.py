import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict


app = FastAPI()

# Agregar el middleware CORS antes de definir tus rutas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Esto permite cualquier origen, debes ajustarlo para producción.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Abre el archivo CSV
data_games = pd.read_csv('limpio_games_gituno.csv')

def encontrar_desarrollador_por_id(id, data_games):
    # Filtrar el DataFrame para encontrar la fila con el ID proporcionado
    fila = data_games[data_games['id'] == id]

    if not fila.empty:
        # Si se encuentra la fila, obtener el nombre del desarrollador asociado
        desarrollador = fila['developer'].iloc[0]
        return desarrollador
    else:
        return "No se encontró un desarrollador para el ID proporcionado."

def developer(desarrollador, data_games):
    
    # Filtrar los elementos asociados a la empresa desarrolladora especificada
    elementos_desarrollador = data_games[data_games['developer'] == desarrollador]

    # Extraer el año (en formato YYYY) de la columna 'release_date'
    elementos_desarrollador['release_year'] = elementos_desarrollador['release_date'].str.extract(r'(\d{4})')

    # Calcular la cantidad de elementos lanzados por año
    elementos_por_año = elementos_desarrollador.groupby('release_year').size().reset_index(name='Cantidad de Items')

    # Calcular el porcentaje de elementos gratuitos por año
    elementos_gratuitos_por_año = elementos_desarrollador[elementos_desarrollador['price'] == 0]
    elementos_gratuitos_por_año = elementos_gratuitos_por_año.groupby('release_year').size().reset_index(name='Contenido Free en %')

    # Fusionar ambos DataFrames para obtener el resultado final
    resultado = elementos_por_año.merge(elementos_gratuitos_por_año, on='release_year', how='left')
    resultado['Contenido Free en %'] = (resultado['Contenido Free en %'] / resultado['Cantidad de Items']) * 100

    return resultado

# Crear un endpoint para obtener resultados por ID
@app.get("/obtener_resultados/{id}")
async def obtener_resultados(id: int = None):
    if id is None:
        return {"mensaje": "Por favor, proporciona un ID válido."}
    
    nombre_del_desarrollador = encontrar_desarrollador_por_id(id, data_games)
    
    if nombre_del_desarrollador == "No se encontró un desarrollador para el ID proporcionado.":
        return {"mensaje": nombre_del_desarrollador}
    
    resultado = developer(nombre_del_desarrollador, data_games)
    
    if not resultado.empty:
        return resultado.to_dict(orient='split')
    else:
        return {"mensaje": "No se encontraron datos para el ID proporcionado."}
    
    
    
app = FastAPI()

# Cargar el archivo CSV una vez al iniciar la aplicación
try:
    data_dos = pd.read_csv('user_data_subset.csv')
except Exception as e:
    raise Exception("Se produjo un error al leer el archivo CSV: " + str(e))

def userdata(user_id: str, data_dos):
    # Filtrar las revisiones del usuario
    user_reviews = data_dos[data_dos['user_id'] == user_id]

    # Filtrar las compras del usuario
    user_purchases = data_dos[data_dos['user_id'] == user_id]

    # Calcular la cantidad total de dinero gastado por el usuario
    user_game_ids = user_purchases['item_id']
    total_money_spent = user_purchases['price'].sum()

    # Calcular el porcentaje de recomendación promedio
    total_recommendation_percentage = user_reviews['recommend'].mean()

    # Contar la cantidad de elementos comprados por el usuario
    num_items_purchased = len(user_purchases)

    user_data = {
        "Usuario": user_id,
        "Dinero gastado": f"{total_money_spent} USD",
        "% de recomendación": f"{total_recommendation_percentage:.2f}%",
        "Cantidad de items": num_items_purchased,
    }

    return user_data

@app.get("/user_data/{user_id}")
async def get_user_data(user_id: str) -> Dict:
    return userdata(user_id, data_dos)
