"""
config.py
=========
Valores de configuración centralizados del framework.

Cualquier dato que pueda cambiar según el entorno (URLs, timeouts, modo headless)
se define acá, para no tener valores "mágicos" repartidos por el código.
"""

import os
from pathlib import Path

# --- Rutas del proyecto ---
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "data"
CARPETA_REPORTES = RAIZ_PROYECTO / "reports"
CARPETA_CAPTURAS = CARPETA_REPORTES / "capturas"

# --- Pruebas de UI (SauceDemo) ---
URL_UI = "https://www.saucedemo.com/"

# Credenciales públicas que SauceDemo publica en su propia pantalla de login.
USUARIO_ESTANDAR = "standard_user"
PASSWORD_ESTANDAR = "secret_sauce"

# Segundos que las esperas explícitas aguardan antes de dar un elemento por ausente.
TIMEOUT_UI = 10


def _env_booleano(nombre, por_defecto=False):
    """Interpreta una variable de entorno como booleano ('1', 'true', 'si', 'yes')."""
    valor = os.getenv(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes")


# Chrome sin interfaz gráfica. Se activa con la variable de entorno HEADLESS=true
# o con la opción de línea de comandos `pytest --headless` (ver conftest.py).
HEADLESS = _env_booleano("HEADLESS")

# --- Pruebas de API (JSONPlaceholder) ---
URL_API = "https://jsonplaceholder.typicode.com"

# Segundos máximos de espera por cada petición HTTP.
TIMEOUT_API = 15
