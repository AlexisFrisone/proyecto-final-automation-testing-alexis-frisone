"""
Pruebas de UI: proceso de compra (checkout).

Los compradores y los formularios incompletos se leen de data/checkout.json.
"""

import pytest

from pages.base_page import convertir_precio
from utils.data_loader import como_parametros, leer_json

pytestmark = [pytest.mark.ui, pytest.mark.checkout]

DATOS_CHECKOUT = leer_json("checkout.json")


@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.parametrize("comprador", como_parametros(DATOS_CHECKOUT["compradores_validos"]))
def test_compra_completa_desde_el_catalogo_hasta_la_confirmacion(inventario, comprador):
    """Flujo completo: agregar productos, revisar carrito, checkout, resumen y confirmación.

    Valida además que el subtotal sea la suma de los precios del catálogo y que el
    total sea subtotal + impuestos.
    """
    # --- Catálogo: agregar los productos del comprador ---
    agregados = [inventario.agregar_por_nombre(nombre) for nombre in comprador["productos"]]
    suma_precios = sum(convertir_precio(p["precio"]) for p in agregados)

    # --- Carrito ---
    carrito = inventario.ir_al_carrito()
    assert sorted(carrito.nombres()) == sorted(comprador["productos"]), (
        "El carrito no contiene los productos agregados"
    )

    # --- Datos del comprador ---
    resumen = carrito.ir_al_checkout().continuar_con_datos(
        comprador["nombre"], comprador["apellido"], comprador["codigo_postal"]
    )

    # --- Resumen del pedido ---
    assert sorted(resumen.nombres()) == sorted(comprador["productos"]), (
        "Los productos del resumen no coinciden con los del carrito"
    )
    assert resumen.subtotal() == pytest.approx(suma_precios), (
        f"Subtotal {resumen.subtotal()} distinto a la suma de precios {suma_precios}"
    )
    assert resumen.impuesto() > 0, "El impuesto debería ser positivo"
    assert resumen.total() == pytest.approx(resumen.subtotal() + resumen.impuesto()), (
        "El total no es subtotal + impuesto"
    )

    # --- Confirmación ---
    completo = resumen.finalizar()
    assert completo.mensaje_confirmacion() == completo.MENSAJE_ESPERADO

    catalogo = completo.volver_al_catalogo()
    assert catalogo.cantidad_en_carrito() == 0, "El carrito debería quedar vacío tras comprar"


@pytest.mark.negativo
@pytest.mark.parametrize("datos", como_parametros(DATOS_CHECKOUT["datos_incompletos"]))
def test_checkout_con_datos_incompletos_muestra_error(inventario, datos):
    """Si falta un dato obligatorio, el checkout avisa cuál y no avanza al resumen."""
    inventario.agregar_por_indice(0)
    informacion = inventario.ir_al_carrito().ir_al_checkout()

    informacion.completar_datos(datos["nombre"], datos["apellido"], datos["codigo_postal"])

    assert informacion.mensaje_error() == datos["mensaje_error"], (
        f"Mensaje inesperado: {informacion.mensaje_error()!r}"
    )
    assert "/checkout-step-two.html" not in informacion.url_actual, (
        "El checkout avanzó al resumen aunque faltaban datos obligatorios"
    )


def test_cancelar_en_el_resumen_conserva_el_carrito(inventario):
    """Cancelar desde el resumen vuelve al catálogo sin perder los productos."""
    producto = inventario.agregar_por_indice(0)
    resumen = inventario.ir_al_carrito().ir_al_checkout().continuar_con_datos(
        "Alexis", "Frisone", "1704"
    )

    catalogo = resumen.cancelar()

    assert catalogo.cantidad_en_carrito() == 1, "Cancelar el checkout no debería vaciar el carrito"
    assert catalogo.ir_al_carrito().nombres() == [producto["nombre"]]
