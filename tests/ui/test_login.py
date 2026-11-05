"""
Pruebas de UI: autenticación en SauceDemo.

Los escenarios de login se leen de data/login_usuarios.csv. Cada fila es un caso:
agregar uno nuevo es sólo sumar una línea al CSV, sin tocar este archivo.
    - resultado = "exito": el usuario debe llegar al catálogo.
    - resultado = "error": la app debe rechazar el acceso con `mensaje_error`.
"""

import pytest

from pages import InventarioPage, LoginPage
from utils import config
from utils.data_loader import como_parametros, leer_csv

pytestmark = [pytest.mark.ui, pytest.mark.login]

CASOS_LOGIN = leer_csv("login_usuarios.csv")
LOGINS_VALIDOS = [caso for caso in CASOS_LOGIN if caso["resultado"] == "exito"]
LOGINS_INVALIDOS = [caso for caso in CASOS_LOGIN if caso["resultado"] == "error"]


@pytest.mark.smoke
@pytest.mark.parametrize("caso", como_parametros(LOGINS_VALIDOS))
def test_login_con_credenciales_validas_lleva_al_catalogo(login_page, caso):
    """Un usuario habilitado inicia sesión y llega a la página de productos."""
    inventario = login_page.iniciar_sesion_exitosa(caso["usuario"], caso["password"])

    assert "/inventory.html" in inventario.url_actual, (
        f"Se esperaba la URL del inventario, se obtuvo: {inventario.url_actual}"
    )
    assert inventario.titulo() == "Products", "El encabezado de la sección no es 'Products'"
    assert inventario.logo() == "Swag Labs", "El logo de la aplicación no es 'Swag Labs'"
    assert not login_page.hay_error(), "El login fue exitoso pero se muestra un error"


@pytest.mark.negativo
@pytest.mark.parametrize("caso", como_parametros(LOGINS_INVALIDOS))
def test_login_con_credenciales_invalidas_muestra_error(login_page, caso):
    """La app rechaza credenciales inválidas con el mensaje adecuado y sin dar acceso."""
    login_page.iniciar_sesion(caso["usuario"], caso["password"])

    mensaje = login_page.mensaje_error()
    assert mensaje == caso["mensaje_error"], (
        f"Mensaje de error inesperado.\n  Esperado: {caso['mensaje_error']!r}\n"
        f"  Obtenido: {mensaje!r}"
    )
    assert "/inventory.html" not in login_page.url_actual, (
        "El sistema concedió acceso con credenciales inválidas"
    )
    assert login_page.formulario_visible(), "El formulario de login debería seguir visible"


@pytest.mark.negativo
def test_cerrar_el_cartel_de_error_permite_reintentar(login_page):
    """La "X" del cartel de error lo quita y el reintento con datos válidos funciona."""
    login_page.iniciar_sesion("", "")
    assert login_page.hay_error(), "Enviar el formulario vacío debería mostrar un error"

    login_page.cerrar_error()
    assert not login_page.hay_error(), "El cartel de error sigue visible después de cerrarlo"

    inventario = login_page.iniciar_sesion_exitosa(
        config.USUARIO_ESTANDAR, config.PASSWORD_ESTANDAR
    )
    assert inventario.titulo() == "Products", "El reintento no llevó al catálogo"


@pytest.mark.negativo
@pytest.mark.parametrize("pagina", ["inventory.html", "cart.html", "checkout-step-one.html"])
def test_acceso_directo_sin_sesion_redirige_al_login(driver, pagina):
    """Abrir una página interna por URL sin sesión vuelve al login con un aviso."""
    driver.get(config.URL_UI + pagina)
    login = LoginPage(driver).esperar_carga()

    assert login.mensaje_error() == (
        f"Epic sadface: You can only access '/{pagina}' when you are logged in."
    ), f"Aviso inesperado al abrir '/{pagina}' sin sesión: {login.mensaje_error()!r}"
    assert pagina not in login.url_actual, f"Se permitió abrir '/{pagina}' sin sesión"


@pytest.mark.smoke
def test_logout_cierra_la_sesion(inventario: InventarioPage):
    """Cerrar sesión vuelve al login y la sesión deja de ser válida."""
    login = inventario.cerrar_sesion()
    assert login.formulario_visible(), "El formulario de login no se muestra tras el logout"

    # Volver al inventario por URL debe exigir iniciar sesión otra vez.
    InventarioPage(inventario.driver).abrir()
    assert login.mensaje_error() == (
        "Epic sadface: You can only access '/inventory.html' when you are logged in."
    ), "Después del logout todavía se puede entrar al inventario"
