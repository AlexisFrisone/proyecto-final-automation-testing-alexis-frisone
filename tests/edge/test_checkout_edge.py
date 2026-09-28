"""
Casos borde del formulario de checkout.

Los campos del checkout no tienen restricciones de formato ni de longitud. Se
prueba que datos poco habituales pero legítimos (acentos, apóstrofes, textos muy
largos, códigos postales alfanuméricos) no bloqueen la compra.
"""

import pytest

import helpers
from helpers import Localizadores


@pytest.mark.carrito
@pytest.mark.edge
def test_checkout_acepta_caracteres_especiales_y_textos_largos(driver_logueado):
    """El checkout avanza con acentos, apóstrofes, 120 caracteres y un CP alfanumérico.

    Validaciones:
        - Se llega al resumen del pedido sin mensajes de error.
        - El producto agregado aparece en el resumen.
    """
    driver = driver_logueado
    producto = helpers.agregar_producto_por_indice(driver, indice=0)
    helpers.ir_al_carrito(driver)
    helpers.ir_al_checkout(driver)

    # --- Acción: datos límite ---
    helpers.completar_datos_checkout(
        driver,
        nombre="Ñandú-O'Brien Güemes",
        apellido="x" * 120,
        codigo_postal="AB-12 34",
    )

    # --- Validación ---
    helpers.esperar_url_contiene(driver, "/checkout-step-two.html")
    assert not helpers.elemento_existe(driver, Localizadores.MENSAJE_ERROR), (
        "El checkout mostró un error con datos válidos poco habituales"
    )
    assert helpers.obtener_nombres_en_carrito(driver) == [producto["nombre"]], (
        "El resumen no muestra el producto agregado"
    )
