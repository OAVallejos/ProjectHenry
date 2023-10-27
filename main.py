
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importa el middleware de CORS

app = FastAPI()

# Agrega el middleware CORS antes de definir tus rutas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Esto permite cualquier origen, debes ajustarlo para producción.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar los datos del archivo CSV al DataFrame
data_games = pd.read_csv('limpio_games.csv')

# Definir la función obtener_tabla_por_id 
def obtener_tabla_por_id(df, id):
    # Filtrar los juegos gratuitos (precio igual a 0) en el DataFrame con el ID proporcionado
    juegos_gratuitos = df[df['price'] == 0]

    # Extraer el año de lanzamiento (solo los últimos 2 dígitos de "YY")
    juegos_gratuitos['año_lanzamiento'] = juegos_gratuitos['release_date'].str[-2:]

    # Contar la cantidad de juegos gratuitos por año
    conteo_por_año = juegos_gratuitos['año_lanzamiento'].value_counts()

    # Calcular el porcentaje de juegos gratuitos por año
    total_juegos_por_año = df['release_date'].str[-2:].value_counts()
    porcentaje_gratuitos_por_año = (conteo_por_año / total_juegos_por_año) * 100

    # Ordenar por año
    porcentaje_gratuitos_por_año = porcentaje_gratuitos_por_año.sort_index()

    # Filtrar los juegos gratuitos (precio igual a 0) nuevamente
    juegos_gratuitos = df[df['price'] == 0]

    # Extraer el año de lanzamiento (solo los últimos 2 dígitos de "YY")
    juegos_gratuitos['año_lanzamiento'] = juegos_gratuitos['release_date'].str[-2:]

    # Agrupar los juegos gratuitos por desarrollador y año de lanzamiento
    gratuitos_por_desarrollador = juegos_gratuitos.groupby(['developer', 'año_lanzamiento']).size().unstack(fill_value=0)

    return porcentaje_gratuitos_por_año, gratuitos_por_desarrollador

# Crear un endpoint para obtener resultados por ID
@app.get("/obtener_resultados/{id}")
async def obtener_resultados(id: str):
    porcentaje_por_año, juegos_por_desarrollador = obtener_tabla_por_id(data_games, id)

    # Crear un diccionario con los resultados
    resultados = {
        'porcentaje_por_año': porcentaje_por_año.to_dict(),
        'juegos_por_desarrollador': juegos_por_desarrollador.to_dict()
    }

    return resultados


