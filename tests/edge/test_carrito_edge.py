"""
Caso borde del carrito de compras.

SauceDemo no muestra el badge con un "0": directamente lo elimina del DOM cuando
el carrito queda vacío. Es una condición límite que rompe los tests escritos con
la suposición de que el elemento siempre existe, y por eso vale la pena cubrirla.
"""

import pytest

import helpers
from helpers import Localizadores


@pytest.mark.carrito
@pytest.mark.edge
def test_el_badge_desaparece_cuando_el_carrito_vuelve_a_estar_vacio(driver_logueado):
    """Al quitar el único producto, el badge del carrito deja de existir en el DOM.

    Pasos:
        1. Agregar el primer producto y confirmar que el badge muestra 1.
        2. Quitarlo con el botón "Remove", que reemplaza al de "Add to cart".
        3. Verificar que el badge ya no esté presente.
        4. Abrir el carrito y confirmar que no contiene ítems.
    """
    driver = driver_logueado

    # --- Estado inicial: sin badge, porque el carrito está vacío ---
    assert not helpers.elemento_existe(driver, Localizadores.BADGE_CARRITO), (
        "El badge no debería existir con el carrito vacío"
    )

    # --- Acción: agregar un producto ---
    helpers.agregar_producto_por_indice(driver, indice=0)
    assert helpers.obtener_contador_carrito(driver) == 1, (
        "El badge debería mostrar 1 después de agregar un producto"
    )

    # --- Acción: quitar el mismo producto ---
    helpers.remover_producto_por_indice(driver, indice=0)

    # --- Validación: el badge desaparece en lugar de mostrar 0 ---
    assert not helpers.elemento_existe(driver, Localizadores.BADGE_CARRITO), (
        "El badge sigue presente después de vaciar el carrito"
    )
    assert helpers.obtener_contador_carrito(driver) == 0, (
        "El contador del carrito no volvió a cero"
    )

    # --- Validación: el carrito efectivamente quedó vacío ---
    helpers.ir_al_carrito(driver)
    assert len(helpers.obtener_nombres_en_carrito(driver)) == 0, (
        "El carrito muestra productos aunque debería estar vacío"
    )
