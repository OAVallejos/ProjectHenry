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

# Abre el archivo CSV
data_games = pd.read_csv('limpio_games_gituno.csv')

def obtener_informacion_desarrollador(data_games, developer_id):
    # Filtrar las filas con precio igual a 0 (contenido gratuito)
    juegos_gratuitos = data_games[data_games['price'] == 0].copy()

    # Extraer el año (en formato YYYY) de la columna 'release_date' y asignar a la copia original
    juegos_gratuitos['release_year'] = juegos_gratuitos['release_date'].str.extract(r'(\d{4})')

    # Filtrar los juegos del desarrollador con el ID proporcionado
    juegos_del_desarrollador = juegos_gratuitos[juegos_gratuitos['developer'] == developer_id]

    # Agrupar por año y contar juegos gratuitos
    agrupado = juegos_del_desarrollador.groupby(['release_year']).agg({'app_name': 'count'})

    # Renombrar la columna
    agrupado = agrupado.rename(columns={'app_name': 'juegos_gratuitos'})

    # Calcular el porcentaje de juegos gratuitos
    total_juegos = len(juegos_del_desarrollador)
    agrupado['porcentaje_gratuitos'] = (agrupado['juegos_gratuitos'] / total_juegos) * 100

    resultado_json = agrupado.to_dict(orient='split')
    return resultado_json

# Crear un endpoint para obtener resultados por ID de desarrollador
@app.get("/obtener_resultados/{developer_id}")
async def obtener_resultados(developer_id: str):
    resultado = obtener_informacion_desarrollador(data_games, developer_id)
    return resultado
