"""
Casos borde del formulario de login.

A diferencia de los negativos (credenciales que existen pero no sirven), acá se
prueban los límites de la validación: campos sin completar y sensibilidad a
mayúsculas. Son situaciones que un usuario real produce sin querer y que suelen
quedar fuera de la cobertura.
"""

import pytest

import helpers
from helpers import Localizadores


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


@pytest.mark.login
@pytest.mark.edge
@pytest.mark.parametrize(
    "usuario, password",
    [
        ("STANDARD_USER", helpers.PASSWORD_VALIDA),
        (helpers.USUARIO_VALIDO, "SECRET_SAUCE"),
    ],
    ids=["usuario_en_mayusculas", "password_en_mayusculas"],
)
def test_login_distingue_mayusculas_y_minusculas(driver, usuario, password):
    """Las credenciales correctas escritas con otras mayúsculas no son válidas.

    Es un límite fácil de pasar por alto (por ejemplo, con Bloq Mayús activado): la
    aplicación debe tratarlas como credenciales distintas y rechazarlas.
    """
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, usuario, password)

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_CREDENCIALES_INVALIDAS, (
        f"Mensaje de error inesperado: '{mensaje}'"
    )
    assert "/inventory.html" not in driver.current_url, (
        "El login aceptó credenciales con mayúsculas distintas"
    )


@pytest.mark.login
@pytest.mark.edge
def test_cerrar_el_cartel_de_error_lo_quita_de_la_pantalla(driver):
    """La "X" del cartel de error lo elimina y permite reintentar el login.

    Pasos:
        1. Provocar un error enviando el formulario vacío.
        2. Cerrar el cartel con su botón.
        3. Verificar que el cartel desaparece.
        4. Reintentar con credenciales válidas y confirmar el acceso.
    """
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, "", "")
    assert helpers.obtener_mensaje_error(driver) == helpers.ERROR_USUARIO_REQUERIDO

    # --- Acción: cerrar el cartel ---
    helpers.esperar_elemento_clickeable(driver, Localizadores.BOTON_CERRAR_ERROR).click()

    # --- Validación: el cartel ya no está ---
    assert not helpers.elemento_existe(driver, Localizadores.MENSAJE_ERROR), (
        "El cartel de error sigue visible después de cerrarlo"
    )

    # --- Validación: se puede reintentar normalmente ---
    helpers.hacer_login(driver, helpers.USUARIO_VALIDO, helpers.PASSWORD_VALIDA)
    helpers.esperar_url_contiene(driver, "/inventory.html")
    assert helpers.obtener_titulo_seccion(driver) == "Products", (
        "El reintento de login no llevó a la página de productos"
    )


@pytest.mark.login
@pytest.mark.edge
def test_login_con_espacios_alrededor_del_usuario_es_rechazado(driver):
    """Un usuario válido con espacios al principio y al final no es aceptado.

    La aplicación no recorta los espacios (típicos al copiar y pegar), así que el
    usuario se considera distinto y se rechaza como credencial inválida.
    """
    helpers.ir_a_login(driver)
    helpers.hacer_login(driver, f"  {helpers.USUARIO_VALIDO}  ", helpers.PASSWORD_VALIDA)

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_CREDENCIALES_INVALIDAS, (
        f"Mensaje de error inesperado: '{mensaje}'"
    )
    assert "/inventory.html" not in driver.current_url, (
        "El login aceptó un usuario con espacios alrededor"
    )
