from fastapi import FastAPI

app = FastAPI()

# main.py

if __name__ == "__main__":
    print("La aplicación se está ejecutando correctamente.")
    # Aquí puedes agregar el código principal de tu aplicación



# Datos de ejemplo (reemplázalos con tus datos reales)
data = {
    "games": [
        {
            "title": "Game A",
            "genre": "Action",
            "year": 2012,
            "playtime": 150
        },
        {
            "title": "Game B",
            "genre": "Adventure",
            "year": 2013,
            "playtime": 200
        },
        # Agrega más datos aquí
    ]
}

# Define tus funciones de endpoints aquí
# Nota: Debes implementar las funciones con lógica real según tus datos

@app.get("/")
def read_root():
    return {"message": "¡API de la empresa!"}

@app.get("/playtime_genre/{genre}")
def playtime_genre(genre: str):
    # Implementa la lógica para encontrar el año con más horas jugadas para el género dado
    # Devuelve un diccionario con el resultado
    # Ejemplo de retorno: {"Año de lanzamiento con más horas jugadas para Género X" : 2013}
    pass

@app.get("/user_for_genre/{genre}")
def user_for_genre(genre: str):
    # Implementa la lógica para encontrar el usuario con más horas jugadas para el género dado
    # y una lista de acumulación de horas jugadas por año
    # Devuelve un diccionario con el resultado
    # Ejemplo de retorno: {"Usuario con más horas jugadas para Género X" : us213ndjss09sdf, "Horas jugadas":[{Año: 2013, Horas: 203}, {Año: 2012, Horas: 100}, {Año: 2011, Horas: 23}]}
    pass

@app.get("/users_recommend/{year}")
def users_recommend(year: int):
    # Implementa la lógica para encontrar el top 3 de juegos MÁS recomendados por usuarios para el año dado
    # Devuelve una lista de diccionarios con el resultado
    # Ejemplo de retorno: [{"Puesto 1" : X}, {"Puesto 2" : Y},{"Puesto 3" : Z}]
    pass

@app.get("/users_not_recommend/{year}")
def users_not_recommend(year: int):
    # Implementa la lógica para encontrar el top 3 de juegos MENOS recomendados por usuarios para el año dado
    # Devuelve una lista de diccionarios con el resultado
    # Ejemplo de retorno: [{"Puesto 1" : X}, {"Puesto 2" : Y},{"Puesto 3" : Z}]
    pass

@app.get("/sentiment_analysis/{year}")
def sentiment_analysis(year: int):
    # Implementa la lógica para el análisis de sentimiento según el año de lanzamiento
    # Devuelve un diccionario con la cantidad de registros de reseñas de usuarios categorizados con análisis de sentimiento
    # Ejemplo de retorno: {Negative = 182, Neutral = 120, Positive = 278}
    pass
