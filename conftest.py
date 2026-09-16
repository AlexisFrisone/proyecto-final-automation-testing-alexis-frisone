"""
conftest.py
===========
Fixtures compartidas por toda la suite y configuración de reportes.

Al estar en la raíz del proyecto, estas fixtures quedan disponibles para los tests
de todas las carpetas (positive, negative, edge y e2e) sin necesidad de importarlas.
"""

import os
from datetime import datetime

import pytest

import helpers


CARPETA_CAPTURAS = os.path.join("reports", "capturas")


@pytest.fixture
def driver():
    """Entrega un navegador limpio a cada caso de prueba y lo cierra al terminar.

    El alcance es de función (el valor por defecto de pytest), de modo que cada test
    arranca con una sesión nueva. Esto evita que el resultado de un test dependa del
    estado que haya dejado otro y permite ejecutarlos en cualquier orden.

    El `yield` garantiza que el navegador se cierre incluso si el test falla.
    """
    navegador = helpers.iniciar_driver()
    yield navegador
    navegador.quit()


@pytest.fixture
def driver_logueado(driver):
    """Entrega un navegador con la sesión ya iniciada, parado en el inventario.

    Evita repetir el login en cada test que no está validando el login en sí mismo.
    """
    helpers.login_exitoso(driver)
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Adjunta una captura de pantalla al reporte HTML cuando un test falla.

    Facilita el diagnóstico: en lugar de leer solo el mensaje de error, se ve el
    estado exacto de la pantalla en el momento del fallo.
    """
    plugin_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    reporte = outcome.get_result()
    extras = getattr(reporte, "extras", [])

    if reporte.when == "call" and reporte.failed and plugin_html is not None:
        navegador = item.funcargs.get("driver")
        if navegador is not None:
            try:
                os.makedirs(CARPETA_CAPTURAS, exist_ok=True)
                marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"{item.name}_{marca_tiempo}.png"
                ruta = os.path.join(CARPETA_CAPTURAS, nombre_archivo)
                navegador.save_screenshot(ruta)
                extras.append(plugin_html.extras.image(ruta))
            except Exception:
                # Una captura fallida nunca debe hacer caer la generación del reporte.
                pass

    reporte.extras = extras
