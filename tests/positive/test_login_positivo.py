"""
Caso positivo: autenticación con credenciales válidas.

Cubre la primera consigna obligatoria de la pre-entrega.
"""

import pytest

import helpers
from helpers import Localizadores


@pytest.mark.login
@pytest.mark.smoke
def test_login_con_credenciales_validas_redirige_al_inventario(driver):
    """El usuario estándar inicia sesión y llega a la página de productos.

    Pasos:
        1. Navegar a la página de login de SauceDemo.
        2. Ingresar las credenciales válidas (standard_user / secret_sauce).
        3. Enviar el formulario.

    Validaciones:
        - La URL cambia a /inventory.html.
        - El encabezado de la sección muestra "Products".
        - El logo de la aplicación muestra "Swag Labs".
        - No aparece ningún mensaje de error.
    """
    # --- Acción ---
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, helpers.USUARIO_VALIDO, helpers.PASSWORD_VALIDA)

    # --- Validación: redirección ---
    helpers.esperar_url_contiene(driver, "/inventory.html")
    assert "/inventory.html" in driver.current_url, (
        f"Se esperaba la URL del inventario, pero se obtuvo: {driver.current_url}"
    )

    # --- Validación: encabezado de la sección ---
    titulo = helpers.obtener_titulo_seccion(driver)
    assert titulo == "Products", f"Se esperaba el título 'Products', se obtuvo '{titulo}'"

    # --- Validación: identidad de la aplicación ---
    logo = helpers.esperar_elemento(driver, Localizadores.LOGO_APP).text
    assert logo == "Swag Labs", f"Se esperaba el logo 'Swag Labs', se obtuvo '{logo}'"

    # --- Validación: ausencia de errores ---
    assert not helpers.elemento_existe(driver, Localizadores.MENSAJE_ERROR), (
        "El login fue exitoso pero la página muestra un mensaje de error"
    )
