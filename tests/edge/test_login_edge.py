"""
Casos borde del formulario de login.

A diferencia de los negativos (credenciales que existen pero no sirven), acá se
prueban los límites de la validación: campos sin completar y sensibilidad a
mayúsculas. Son situaciones que un usuario real produce sin querer y que suelen
quedar fuera de la cobertura.
"""

import pytest

import helpers


@pytest.mark.login
@pytest.mark.edge
def test_login_con_ambos_campos_vacios_exige_el_usuario(driver):
    """Enviar el formulario vacío reclama primero el campo usuario.

    La aplicación valida en orden: aunque falten los dos datos, el mensaje que
    devuelve es el del campo usuario. El test documenta ese comportamiento.
    """
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, "", "")

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_USUARIO_REQUERIDO, (
        f"Se esperaba el aviso de usuario requerido, se obtuvo: '{mensaje}'"
    )


@pytest.mark.login
@pytest.mark.edge
def test_login_sin_password_exige_la_contrasena(driver):
    """Con el usuario cargado pero la contraseña vacía, se reclama la contraseña.

    Complementa el caso anterior: confirma que la validación avanza al segundo campo
    una vez que el primero está completo.
    """
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, helpers.USUARIO_VALIDO, "")

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_PASSWORD_REQUERIDA, (
        f"Se esperaba el aviso de contraseña requerida, se obtuvo: '{mensaje}'"
    )

    assert "/inventory.html" not in driver.current_url, (
        "El sistema permitió el acceso sin contraseña"
    )
