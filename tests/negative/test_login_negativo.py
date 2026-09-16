"""
Casos negativos: escenarios en los que la aplicación debe rechazar el acceso.

Un test negativo no verifica que algo funcione, sino que el sistema falle de la
forma correcta: mostrando el mensaje adecuado y sin conceder acceso.
"""

import pytest

import helpers
from helpers import Localizadores


@pytest.mark.login
@pytest.mark.negativo
def test_login_con_password_incorrecta_muestra_error(driver):
    """Un usuario válido con contraseña incorrecta no puede ingresar.

    Validaciones:
        - Se muestra el mensaje de credenciales inválidas.
        - La URL sigue siendo la de login, sin redirección al inventario.
    """
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, helpers.USUARIO_VALIDO, helpers.PASSWORD_INVALIDA)

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_CREDENCIALES_INVALIDAS, (
        f"Mensaje de error inesperado: '{mensaje}'"
    )

    assert "/inventory.html" not in driver.current_url, (
        "El sistema permitió el acceso con una contraseña incorrecta"
    )


@pytest.mark.login
@pytest.mark.negativo
def test_login_con_usuario_bloqueado_muestra_error_especifico(driver):
    """El usuario bloqueado recibe un mensaje distinto al de credenciales inválidas.

    Es un escenario relevante porque las credenciales son correctas: lo que falla es
    el estado de la cuenta. La aplicación debe distinguir ambos casos.
    """
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, helpers.USUARIO_BLOQUEADO, helpers.PASSWORD_VALIDA)

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_USUARIO_BLOQUEADO, (
        f"Se esperaba el aviso de usuario bloqueado, se obtuvo: '{mensaje}'"
    )

    assert "/inventory.html" not in driver.current_url, (
        "Un usuario bloqueado logró acceder al inventario"
    )


@pytest.mark.login
@pytest.mark.negativo
def test_login_con_usuario_inexistente_no_revela_si_el_usuario_existe(driver):
    """Un usuario que no existe recibe el mismo mensaje que una contraseña errónea.

    Esto es intencional desde el punto de vista de seguridad: mensajes distintos
    permitirían a un atacante averiguar qué nombres de usuario son válidos.
    """
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, helpers.USUARIO_INEXISTENTE, helpers.PASSWORD_VALIDA)

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_CREDENCIALES_INVALIDAS, (
        f"Mensaje de error inesperado: '{mensaje}'"
    )

    assert helpers.elemento_existe(driver, Localizadores.CAMPO_USUARIO), (
        "El formulario de login debería seguir visible tras el intento fallido"
    )
