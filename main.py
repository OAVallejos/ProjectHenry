import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import json
from pydantic import BaseModel
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder




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

def process_developer(desarrollador: str, data_games: pd.DataFrame):
    # Filtrar los elementos asociados a la empresa desarrolladora especificada
    elementos_desarrollador = data_games[data_games['developer'] == desarrollador]

    if elementos_desarrollador.empty:
        return "No se encontraron elementos para la empresa desarrolladora especificada."

    # Convert 'release_year' column to native Python integers
    elementos_desarrollador['release_year'] = elementos_desarrollador['release_date'].str.extract(r'(\d{4})')

    # Calcular la cantidad de elementos lanzados por año
    elementos_por_anio = elementos_desarrollador['release_year'].value_counts().reset_index()
    elementos_por_anio.columns = ['Anio', 'Cantidad de Items']

    # Calcular el porcentaje de elementos gratuitos por año
    elementos_gratuitos_por_anio = elementos_desarrollador[elementos_desarrollador['price'] == 0]
    elementos_gratuitos_por_anio = elementos_gratuitos_por_anio['release_year'].value_counts().reset_index()
    elementos_gratuitos_por_anio.columns = ['Anio', 'Contenido Free en %']

    # Fusionar ambos DataFrames para obtener el resultado final
    resultado = elementos_por_anio.merge(elementos_gratuitos_por_anio, on='Anio', how='left')
    resultado['Contenido Free en %'] = (resultado['Contenido Free en %'] / resultado['Cantidad de Items']) * 100

    # Reemplazar NaN, Infinity y -Infinity por None
    resultado = resultado.replace([np.inf, -np.inf, np.nan], None)

    # Convertir DataFrame a diccionario de Python
    resultado_dict = resultado.to_dict()

    # Convertir diccionario de Python a JSON
    resultado_json = json.dumps(resultado_dict, separators=(",", ":"))

    return resultado_json

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



# Modelo



# Definir la clase JuegoFicticio para el objeto de entrada
class JuegoFicticio(BaseModel):
    sentiment_analysis: int
    items_count: int
    price: int


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar el archivo CSV con los datos
tablas = pd.read_csv('modelo.csv')

# Usamos factorize para asignar índices a las etiquetas únicas en la columna 'genres'
tablas['genres'], genre_index = tablas['genres'].factorize()

def entrenar_modelo(tablas):
    # Divide los datos en características (X) y etiquetas (y)
    X = tablas.drop('genres', axis=1)  # Excluye la columna 'genres' como característica
    y = tablas['genres']

    # Divide los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Selecciona las características numéricas
    columnas_numericas = ['sentiment_analysis', 'items_count', 'price']

    # Escala solo las características numéricas
    scaler = StandardScaler()
    X_train_numerico = scaler.fit_transform(X_train[columnas_numericas])
    X_test_numerico = scaler.transform(X_test[columnas_numericas])

    # Diseña la arquitectura de la red neuronal
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(X_train_numerico.shape[1],)))  # Capa de entrada
    model.add(keras.layers.Dense(64, activation='relu'))  # Capa oculta 1
    model.add(keras.layers.Dense(32, activation='relu'))  # Capa oculta 2
    model.add(keras.layers.Dense(len(y.unique()), activation='softmax'))  # Capa de salida

    # Compila el modelo
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Entrena el modelo
    model.fit(X_train_numerico, y_train, epochs=10, batch_size=32, validation_split=0.2)

    # Evalúa el modelo
    score = model.evaluate(X_test_numerico, y_test)

    # Devuelve el modelo entrenado, el escalador y las columnas numéricas
    return model, scaler, columnas_numericas

# Llama a la función para entrenar el modelo
model, scaler, columnas_numericas = entrenar_modelo(tablas)








# Endpoint
@app.get("/developer/{developer}")
async def get_developer(developer: str):
    resultado_json = process_developer(developer, data_games)
    return resultado_json

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





# Enruta al punto final para realizar predicciones
@app.get("/predecir_genero/")
async def predecir_genero(juego: JuegoFicticio):
    # Escalar las características del nuevo juego
    juego_numerico = np.array([[juego.sentiment_analysis, juego.items_count, juego.price]])
    juego_numerico = scaler.transform(juego_numerico)

    # Realizar la predicción del género
    prediccion = model.predict(juego_numerico)

    # Encontrar la categoría de género con la probabilidad más alta
    categoria_genero_predicha = genre_index[np.argmax(prediccion)]

    # Devolver la categoría de género predicha
    return {"Categoría de género predicha": categoria_genero_predicha}
