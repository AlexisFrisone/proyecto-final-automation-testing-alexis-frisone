"""
Pruebas de UI de punta a punta que atraviesan varias pantallas.

Buscan problemas de integración entre pantallas que los tests aislados no detectan:
el login, el catálogo, el carrito y el checkout tienen que funcionar en conjunto.
"""

import pytest

from pages import LoginPage
from utils import config

pytestmark = [pytest.mark.ui, pytest.mark.e2e]


def _comprar(catalogo, indice):
    """Compra el producto de la posición indicada y devuelve (producto, pantalla final)."""
    producto = catalogo.agregar_por_indice(indice)
    resumen = catalogo.ir_al_carrito().ir_al_checkout().continuar_con_datos(
        "Alexis", "Frisone", "1704"
    )
    return producto, resumen.finalizar()


def test_ordenar_por_precio_y_comprar_el_producto_mas_barato(inventario):
    """El primer producto tras ordenar por precio ascendente es el más barato y se cobra eso."""
    precio_minimo = min(inventario.precios())

    inventario.ordenar(inventario.ORDEN_PRECIO_ASC)
    inventario.agregar_por_indice(0)

    resumen = inventario.ir_al_carrito().ir_al_checkout().continuar_con_datos(
        "Alexis", "Frisone", "1704"
    )
    assert resumen.subtotal() == pytest.approx(precio_minimo), (
        f"El subtotal ({resumen.subtotal()}) no es el precio mínimo ({precio_minimo})"
    )
    assert resumen.finalizar().mensaje_confirmacion() == "Thank you for your order!"


def test_seguir_comprando_desde_el_carrito_antes_de_pagar(inventario):
    """El botón "Continue Shopping" permite sumar productos y ambos llegan al resumen."""
    primero = inventario.agregar_por_indice(0)
    catalogo = inventario.ir_al_carrito().seguir_comprando()
    segundo = catalogo.agregar_por_indice(3)

    esperados = sorted([primero["nombre"], segundo["nombre"]])
    carrito = catalogo.ir_al_carrito()
    assert sorted(carrito.nombres()) == esperados

    resumen = carrito.ir_al_checkout().continuar_con_datos("Alexis", "Frisone", "1704")
    assert sorted(resumen.nombres()) == esperados
    assert resumen.finalizar().mensaje_confirmacion() == "Thank you for your order!"


def test_dos_compras_consecutivas_en_la_misma_sesion(inventario):
    """Después de una compra se puede hacer otra sin volver a iniciar sesión."""
    catalogo = inventario
    for numero_compra, indice in ((1, 0), (2, 4)):
        _, completo = _comprar(catalogo, indice)
        assert completo.mensaje_confirmacion() == "Thank you for your order!"

        catalogo = completo.volver_al_catalogo()
        assert catalogo.cantidad_en_carrito() == 0, f"Compra {numero_compra}: carrito no vacío"
        assert all(t == "Add to cart" for t in catalogo.textos_botones()), (
            f"Compra {numero_compra}: quedaron botones en 'Remove'"
        )


def test_el_carrito_sobrevive_a_un_logout_y_se_completa_la_compra(inventario):
    """SauceDemo guarda el carrito en el navegador: tras logout y login sigue intacto."""
    agregados = sorted(inventario.agregar_por_indice(i)["nombre"] for i in (0, 1))

    login = inventario.cerrar_sesion()
    catalogo = login.iniciar_sesion_exitosa(config.USUARIO_ESTANDAR, config.PASSWORD_ESTANDAR)

    assert catalogo.esperar_cantidad_en_carrito(2) == 2, "El carrito no se conservó"
    carrito = catalogo.ir_al_carrito()
    assert sorted(carrito.nombres()) == agregados

    resumen = carrito.ir_al_checkout().continuar_con_datos("Alexis", "Frisone", "1704")
    assert sorted(resumen.nombres()) == agregados
    assert resumen.finalizar().mensaje_confirmacion() == "Thank you for your order!"


def test_usuario_bloqueado_no_puede_comprar(driver):
    """Un usuario bloqueado se queda en el login y no accede a ninguna pantalla interna."""
    login = LoginPage(driver).abrir()
    login.iniciar_sesion("locked_out_user", config.PASSWORD_ESTANDAR)

    assert "locked out" in login.mensaje_error()

    driver.get(config.URL_UI + "cart.html")
    assert LoginPage(driver).esperar_carga().formulario_visible(), (
        "Un usuario bloqueado no debería poder abrir el carrito"
    )
