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

# PRIMER CONSULTA Abre el archivo CSV
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

# SEGUNDA CONSULTA Cargar el archivo CSV una vez al iniciar la aplicación
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

# TERCERA CONSULTA Cargar los archivos CSV una vez al iniciar la aplicación
data_reviews_nuevo = pd.read_csv('data_reviews_endtres.csv')
data_games_nuevo = pd.read_csv('data_games_endtres.csv')


def UserForGenre(data_games_nuevo, data_reviews_nuevo, genre):
    # Paso 1: Filtrar los juegos del género específico en data_games
    genre_filter = data_games_nuevo['genres'].str.contains(genre, case=False, na=False)
    genre_games = data_games_nuevo[genre_filter]

    if genre_games.empty:
        return f"No se encontraron juegos en el género '{genre}'"

    # Paso : Filtrar las reseñas en data_reviews que corresponden a estos juegos
    genre_reviews = data_reviews_nuevo[data_reviews_nuevo['item_id'].isin(genre_games['id'])]

    # Paso : Calcular la cantidad total de horas jugadas por año de lanzamiento en las reseñas
    playtime_by_year = genre_reviews.groupby('year_posted')['sentiment_analysis'].count().reset_index()
    playtime_by_year.columns = ['Año', 'Horas']

    # Paso : Encontrar el usuario con más horas jugadas y construir el resultado deseado
    max_user_id = genre_reviews.groupby('user_id')['sentiment_analysis'].count().idxmax()
    
    result = {
        "Usuario con más horas jugadas para género": max_user_id,
        "Horas jugadas": playtime_by_year.to_dict(orient='records')
    }

    return result


# CUARTA 4 CONSULTA 
result = pd.read_csv('resultados_endcuatro.csv')


def mejores_desarrolladores_anio(anio: int):
    # Paso 1: Filtrar las revisiones para el año proporcionado y donde recommend es True y sentiment_analysis es positivo
    revisiones_filtradas = result[(result['year_posted'] == anio) &
                                  (result['recommend'] == True) &
                                  (result['sentiment_analysis'] > 0)]

    # Paso 2: Agrupar por desarrollador y contar la cantidad de juegos recomendados
    desarrolladores_recomendados = revisiones_filtradas.groupby('developer')['recommend'].count().reset_index()

    # Paso 3: Ordenar en orden descendente y tomar el top 3
    top_desarrolladores = desarrolladores_recomendados.sort_values(by='recommend', ascending=False).head(3)

    # Verificar si top_desarrolladores tiene al menos 3 elementos
    if len(top_desarrolladores) >= 3:
        resultado = [{"Puesto " + str(i + 1): top_desarrolladores.iloc[i]['developer']} for i in range(3)]
    else:
        resultado = [{"Puesto " + str(i + 1): "No disponible"} for i in range(len(top_desarrolladores))]

    return resultado

# QUINTA CONSULTA
# Cargar el archivo CSV en un nuevo DataFrame
resultado = pd.read_csv('resultado_endcinco.csv')

# Define la función que toma el nombre del desarrollador como entrada
def developer_reviews_analysis(desarrolladora):
    # Filtra las reseñas para el desarrollador especificado
    developer_data = resultado[resultado['developer'] == desarrolladora]

    # Contar la cantidad de reseñas positivas, negativas y neutras para ese desarrollador
    total_reviews = len(developer_data)
    positive_reviews = (developer_data['sentiment_analysis'] == 2).sum()
    negative_reviews = (developer_data['sentiment_analysis'] == 0).sum()
    neutral_reviews = (developer_data['sentiment_analysis'] == 1).sum()
    
    # Convertir los resultados a enteros
    positive_reviews = int(positive_reviews)
    negative_reviews = int(negative_reviews)
    neutral_reviews = int(neutral_reviews)

    # Devuelve la información del desarrollador como un diccionario
    analysis_result = {
        "desarrolladora": desarrolladora,
        "total_resenias": total_reviews,
        "positive_reviews": positive_reviews,
        "negative_reviews": negative_reviews,
        "neutral_reviews": neutral_reviews
    }

    # Retorna el resultado
    return analysis_result






# Crear un endpoint para obtener resultados 
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

@app.get("/user_data/{user_id}")
async def get_user_data(user_id: str) -> Dict:
    return userdata(user_id, data_dos)


@app.get("/user_for_genre/{genre}")
async def get_user_for_genre(genre: str):
    resultado = UserForGenre(data_games_nuevo, data_reviews_nuevo, genre)
    return resultado


@app.get("/mejores_desarrolladores_año/{anio}")
async def obtener_mejores_desarrolladores_anio(anio: int):
    resultado = mejores_desarrolladores_anio(anio)
    return resultado


@app.get("/analizar_desarrollador/{desarrolladora}")
async def analizar_desarrollador(desarrolladora: str):
    analysis_result = developer_reviews_analysis(desarrolladora)
    return analysis_result
