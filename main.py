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

def obtener_informacion_desarrollador(data_games, pregunta):
    # Filtrar las filas con precio igual a 0 (contenido gratuito)
    juegos_gratuitos = data_games[data_games['price'] == 0].copy()

    # Extraer el año (en formato YYYY) de la columna 'release_date' y asignar a la copia original
    juegos_gratuitos['release_year'] = juegos_gratuitos['release_date'].str.extract(r'(\d{4})')

    # Agrupar por año y empresa desarrolladora, contar juegos gratuitos y juegos totales
    agrupado = juegos_gratuitos.groupby(['release_year', 'developer']).agg({'app_name': 'count'})

    # Renombrar la columna
    agrupado = agrupado.rename(columns={'app_name': 'juegos_gratuitos'})

    # Calcular el total de juegos por año y empresa
    total_juegos = data_games.groupby(['release_date', 'developer']).agg({'app_name': 'count'})
    total_juegos = total_juegos.rename(columns={'app_name': 'total_juegos'})

    # Unir los DataFrames
    resultado = agrupado.join(total_juegos)

    # Calcular el porcentaje de juegos gratuitos
    resultado['porcentaje_gratuitos'] = (resultado['juegos_gratuitos'] / resultado['total_juegos']) * 100
    if pregunta == "ID_del_desarrollador_con_más_juegos_gratuitos":
        # Encontrar el ID del desarrollador con más juegos gratuitos lanzados
        id_desarrollador_mas_juegos_gratuitos = resultado['juegos_gratuitos'].idxmax()
        return {"ID_del_desarrollador_con_más_juegos_gratuitos": id_desarrollador_mas_juegos_gratuitos}
    else:
        # En tu función obtener_resultados
        resultado_json = resultado.to_dict(orient='split')
        return resultado_json

# Crear un endpoint para obtener resultados por ID
@app.get("/obtener_resultados/{id}")
async def obtener_resultados(id: str):
    pregunta = 'Cuál es el porcentaje de juegos gratuitos lanzados por año y desarrolladora'
    resultado = obtener_informacion_desarrollador(data_games, pregunta)
    return resultado
