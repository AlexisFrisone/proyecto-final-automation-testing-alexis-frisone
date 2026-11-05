"""
conftest.py
===========
Fixtures compartidas por toda la suite y personalización del reporte HTML.

Al estar en la raíz del proyecto, todo lo definido acá queda disponible para los
tests de UI y de API sin necesidad de importarlo.

Contenido:
    - Opción `--headless` para correr Chrome sin ventana.
    - Fixtures de UI: `driver`, `login_page`, `inventario`.
    - Fixture de API: `api`.
    - Registro en el log del inicio y fin de cada test.
    - Captura de pantalla automática cuando falla un test de UI, guardada en
      reports/capturas/ y embebida en el reporte HTML.
    - Columna "Descripción" en el reporte, tomada del docstring de cada test.
"""

import html
import re
from datetime import datetime

import pytest

from pages import LoginPage
from utils import config
from utils.api_client import ApiClient
from utils.driver_factory import crear_driver
from utils.logger import obtener_logger

log = obtener_logger("conftest")


# ---------------------------------------------------------------------------
# Opciones de línea de comandos
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Ejecuta Chrome sin interfaz gráfica (también se activa con HEADLESS=true).",
    )


# ---------------------------------------------------------------------------
# Fixtures de UI
# ---------------------------------------------------------------------------

@pytest.fixture
def driver(request):
    """Entrega un navegador nuevo a cada test y lo cierra al terminar.

    El alcance es de función: cada test arranca con una sesión limpia, así el
    resultado de uno nunca depende del estado que dejó otro y se pueden correr en
    cualquier orden. El `try/finally` garantiza que Chrome se cierre siempre.
    """
    headless = request.config.getoption("--headless") or config.HEADLESS
    navegador = crear_driver(headless=headless)
    try:
        yield navegador
    finally:
        log.info("Cerrando el navegador")
        navegador.quit()


@pytest.fixture
def login_page(driver):
    """Navegador parado en la pantalla de login, listo para completar el formulario."""
    return LoginPage(driver).abrir()


@pytest.fixture
def inventario(login_page):
    """Sesión ya iniciada con el usuario estándar, parada en el catálogo.

    Evita repetir el login en los tests que no están validando el login en sí.
    """
    return login_page.iniciar_sesion_exitosa(config.USUARIO_ESTANDAR, config.PASSWORD_ESTANDAR)


# ---------------------------------------------------------------------------
# Fixtures de API
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api():
    """Cliente HTTP para JSONPlaceholder, compartido por todos los tests de API.

    Se comparte a nivel sesión porque no guarda estado entre peticiones (sólo reutiliza
    la conexión), por lo que no compromete la independencia de los tests.
    """
    cliente = ApiClient()
    yield cliente
    cliente.cerrar()


# ---------------------------------------------------------------------------
# Logging de cada test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def registrar_inicio_y_fin(request):
    """Deja en el log una marca de inicio y fin de cada test, para ubicarlos rápido."""
    log.info("===== INICIO: %s =====", request.node.nodeid)
    yield
    log.info("===== FIN: %s =====", request.node.nodeid)


# ---------------------------------------------------------------------------
# Capturas de pantalla y reporte HTML
# ---------------------------------------------------------------------------

def _nombre_archivo_seguro(texto):
    """Reemplaza los caracteres no válidos en nombres de archivo (por ejemplo '[' o ':')."""
    return re.sub(r"[^\w\-]+", "_", texto).strip("_")


def _guardar_captura(navegador, nombre_test):
    """Guarda la pantalla actual en reports/capturas/ y la devuelve en base64.

    El nombre incluye el test y la fecha/hora, por ejemplo:
        test_login_exitoso_usuario_estandar_20261104_213015.png
    """
    config.CARPETA_CAPTURAS.mkdir(parents=True, exist_ok=True)
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = config.CARPETA_CAPTURAS / f"{_nombre_archivo_seguro(nombre_test)}_{marca_tiempo}.png"
    navegador.save_screenshot(str(ruta))
    log.error("Test fallido: captura guardada en %s", ruta)
    return navegador.get_screenshot_as_base64()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Completa el resultado de cada test con la descripción y, si falló, una captura.

    La captura se toma tanto si falla el cuerpo del test como su preparación (por
    ejemplo, un login que no llega al inventario dentro de la fixture).
    """
    outcome = yield
    reporte = outcome.get_result()

    # Primera línea del docstring, para la columna "Descripción" del reporte.
    docstring = (item.function.__doc__ or "").strip()
    reporte.descripcion = docstring.splitlines()[0] if docstring else ""

    if reporte.when not in ("setup", "call") or not reporte.failed:
        return

    navegador = item.funcargs.get("driver")
    plugin_html = item.config.pluginmanager.getplugin("html")
    if navegador is None:
        return

    try:
        imagen_base64 = _guardar_captura(navegador, item.name)
    except Exception as error:  # Una captura fallida nunca debe romper el reporte.
        log.warning("No se pudo tomar la captura de pantalla: %s", error)
        return

    if plugin_html is not None:
        extras = getattr(reporte, "extras", [])
        extras.append(plugin_html.extras.image(imagen_base64, name="Captura del fallo"))
        extras.append(plugin_html.extras.url(navegador.current_url, name="URL al fallar"))
        reporte.extras = extras


def pytest_html_report_title(report):
    report.title = "Reporte de pruebas automatizadas — SauceDemo (UI) y JSONPlaceholder (API)"


def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([
        f"<p><strong>UI:</strong> {config.URL_UI} &nbsp;|&nbsp; "
        f"<strong>API:</strong> {config.URL_API}</p>",
        "<p>Los tests fallidos de UI incluyen una captura de pantalla de la pantalla en el "
        "momento del error. El log completo de la ejecución está en "
        "<code>reports/ejecucion.log</code>.</p>",
    ])


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Descripción</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(2, f"<td>{html.escape(getattr(report, 'descripcion', ''))}</td>")
