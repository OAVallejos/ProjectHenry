import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Agregar el middleware CORS antes de definir tus rutas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Esto permite cualquier origen, debes ajustarlo para producción.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar el archivo CSV una vez al iniciar la aplicación
data_games = pd.read_csv('limpio_games_gituno.csv')

# Función para buscar el desarrollador por ID
def encontrar_desarrollador_por_id(id, data):
    fila = data[data['id'] == id]
    if not fila.empty:
        return fila['developer'].iloc[0]
    return None

# Función para procesar datos del desarrollador
def procesar_desarrollador(desarrollador, data):
    elementos_desarrollador = data[data['developer'] == desarrollador]
    if elementos_desarrollador.empty:
        return None

    elementos_desarrollador['release_year'] = elementos_desarrollador['release_date'].str.extract(r'(\d{4})')
    
    elementos_por_año = elementos_desarrollador.groupby('release_year').size().reset_index(name='Cantidad de Items')
    
    elementos_gratuitos_por_año = elementos_desarrollador[elementos_desarrollador['price'] == 0]
    elementos_gratuitos_por_año = elementos_gratuitos_por_año.groupby('release_year').size().reset_index(name='Contenido Free en %')
    
    resultado = elementos_por_año.merge(elementos_gratuitos_por_año, on='release_year', how='left')
    resultado['Contenido Free en %'] = (resultado['Contenido Free en %'] / resultado['Cantidad de Items']) * 100

    return resultado

# Crear un endpoint para obtener resultados por ID
@app.get("/obtener_resultados/{id}")
async def obtener_resultados(id: int = None):
    if id is None:
        return {"mensaje": "Por favor, proporciona un ID válido."}
    
    nombre_del_desarrollador = encontrar_desarrollador_por_id(id, data_games)
    
    if nombre_del_desarrollador is None:
        return {"mensaje": "No se encontró un desarrollador para el ID proporcionado."}
    
    resultado = procesar_desarrollador(nombre_del_desarrollador, data_games)
    
    if resultado is not None:
        return resultado.to_dict(orient='split')
    else:
        return {"mensaje": "No se encontraron datos para el ID proporcionado."}
