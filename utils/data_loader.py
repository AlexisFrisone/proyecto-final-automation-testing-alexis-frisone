"""
data_loader.py
==============
Lectura de datos de prueba desde archivos externos (CSV y JSON) ubicados en data/.

Separar los datos del código permite agregar nuevos escenarios editando un archivo,
sin tocar los tests: cada fila/objeto se convierte en una ejecución parametrizada.
"""

import csv
import json

from utils.config import CARPETA_DATOS


def leer_csv(nombre_archivo):
    """Devuelve las filas de un CSV de data/ como una lista de diccionarios.

    Las celdas vacías se conservan como cadena vacía (''), lo que permite modelar
    casos como "usuario sin completar".
    """
    ruta = CARPETA_DATOS / nombre_archivo
    with open(ruta, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def leer_json(nombre_archivo):
    """Devuelve el contenido de un JSON de data/ ya deserializado."""
    ruta = CARPETA_DATOS / nombre_archivo
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def como_parametros(registros, campo_id="caso"):
    """Convierte una lista de diccionarios en parámetros de pytest con IDs legibles.

    Cada registro se entrega al test como un único diccionario, y el valor de
    `campo_id` se usa como identificador visible en la salida y en el reporte, por
    ejemplo `test_login_exitoso[usuario_estandar]`.
    """
    import pytest  # Import local: este módulo también se usa fuera de pytest.

    return [pytest.param(registro, id=registro[campo_id]) for registro in registros]
