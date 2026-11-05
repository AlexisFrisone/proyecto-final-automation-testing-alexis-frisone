"""
driver_factory.py
=================
Creación del navegador que usan las pruebas de UI.

A partir de Selenium 4.6, Selenium Manager descarga y configura ChromeDriver
automáticamente, por lo que no hace falta instalar el driver a mano.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.logger import obtener_logger

log = obtener_logger("driver")


def crear_driver(headless=False):
    """Crea y devuelve una instancia de Chrome lista para usar.

    Con `headless=True` el navegador corre sin ventana, lo que se necesita en
    servidores de integración continua como GitHub Actions.
    """
    opciones = Options()
    # Silencia los mensajes de consola de ChromeDriver, que ensucian la salida de pytest.
    opciones.add_experimental_option("excludeSwitches", ["enable-logging"])
    # Desactiva el gestor de contraseñas de Chrome. Como "secret_sauce" figura en
    # filtraciones públicas, Chrome abre el aviso "Cambiá tu contraseña" después del
    # login; ese popup le roba el foco a la página y hace que se pierdan clics.
    opciones.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    opciones.add_argument("--disable-features=PasswordLeakDetection")

    if headless:
        opciones.add_argument("--headless=new")
        opciones.add_argument("--window-size=1920,1080")
        # Necesarios para correr Chrome dentro de contenedores Linux (CI).
        opciones.add_argument("--no-sandbox")
        opciones.add_argument("--disable-dev-shm-usage")
    else:
        opciones.add_argument("--start-maximized")

    log.info("Iniciando Chrome (headless=%s)", headless)
    return webdriver.Chrome(options=opciones)
