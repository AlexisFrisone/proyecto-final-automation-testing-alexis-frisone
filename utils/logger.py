"""
logger.py
=========
Punto único para obtener loggers del framework.

La configuración de formato, nivel y archivo de salida la hace pytest a partir de
pytest.ini (`log_file`, `log_level`, ...). Así, todo lo que se registra:
    - queda en `reports/ejecucion.log` con nivel DEBUG, y
    - aparece en la sección "Captured log" de cada test dentro del reporte HTML.
"""

import logging

# Prefijo común para identificar los mensajes del framework en el log.
PREFIJO = "framework"


def obtener_logger(nombre):
    """Devuelve un logger hijo de 'framework', por ejemplo 'framework.pages.LoginPage'."""
    return logging.getLogger(f"{PREFIJO}.{nombre}")
