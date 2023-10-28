import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajusta esto para la configuración de producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar el archivo CSV una vez al iniciar la aplicación
try:
    data_games = pd.read_csv('limpio_games_gituno.csv')
except Exception as e:
    raise Exception("Se produjo un error al leer el archivo CSV: " + str(e))

# Función para buscar el desarrollador por ID
def encontrar_desarrollador_por_id(id, data):
    # Convertir id a un número
    id = int(id)
    
    fila = data[data['id'] == id]
    if not fila.empty:
        return fila['developer'].iloc[0]
    return None

# Función para procesar datos del desarrollador
def procesar_desarrollador(desarrollador, data):
    elementos_desarrollador = data[data['developer'] == desarrollador]
    if elementos_desarrollador.empty:
        return {"mensaje": "No se encontraron elementos para el desarrollador proporcionado."}

    elementos_desarrollador['release_year'] = elementos_desarrollador['release_date'].str.extract(r'(\d{4})')
    
    elementos_por_año = elementos_desarrollador.groupby('release_year').size().reset_index(name='Cantidad de Items')
    
    elementos_gratuitos_por_año = elementos_desarrollador[elementos_desarrollador['price'] == 0]
    elementos_gratuitos_por_año = elementos_gratuitos_por_año.groupby('release_year').size().reset_index(name='Contenido Free en %')
    
    resultado = elementos_por_año.merge(elementos_gratuitos_por_año, on='release_year', how='left')
    resultado['Contenido Free en %'] = (resultado['Contenido Free en %'] / resultado['Cantidad de Items']) * 100

    # Verificar si el resultado es None
    if resultado is None:
        return {"mensaje": "No se pudo calcular el resultado para el desarrollador proporcionado."}

    # Reemplazar NaN e Infinity con None
    resultado = resultado.where(pd.notnull(resultado), None)
    resultado = resultado.replace([np.inf, -np.inf], None)

    return resultado

# Modelo de datos para la solicitud
class Item(BaseModel):
    value: float

# Modificada la función "calculate" para verificar el rango de los valores
@app.post("/calculate")
def calculate(items: List[Item]):
    # Verificar el rango de los valores antes de llamar a perform_calculation
    if not items:
        raise HTTPException(status_code=400, detail="La lista de items está vacía")
    
    for item in items:
        if item.value < -3.4e38 or item.value > 3.4e38:
            raise HTTPException(status_code=400, detail="Invalid input data: Value is out of range")
    
    try:
        result = perform_calculation(items)
        return {"result": result}
    except ValueError as ve:
        return {}
