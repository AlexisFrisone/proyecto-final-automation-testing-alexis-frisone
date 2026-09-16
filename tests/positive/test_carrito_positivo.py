"""
Caso positivo: interacción con productos y carrito de compras.

Cubre la tercera consigna obligatoria de la pre-entrega.
"""

import pytest

import helpers


@pytest.mark.carrito
@pytest.mark.smoke
def test_agregar_primer_producto_actualiza_carrito(driver_logueado):
    """Agregar un producto incrementa el contador y el ítem aparece en el carrito.

    Pasos:
        1. Agregar al carrito el primer producto del catálogo.
        2. Verificar que el contador del carrito pase de 0 a 1.
        3. Navegar al carrito de compras.
        4. Verificar que el producto agregado figure en el detalle.

    El nombre del producto no está hardcodeado: se lee del catálogo antes de agregarlo
    y se compara contra lo que muestra el carrito.
    """
    driver = driver_logueado

    # --- Estado inicial: el carrito arranca vacío ---
    assert helpers.obtener_contador_carrito(driver) == 0, (
        "El carrito debería estar vacío al iniciar sesión"
    )

    # --- Acción: agregar el primer producto ---
    producto_agregado = helpers.agregar_producto_por_indice(driver, indice=0)

    # --- Validación: el contador se incrementa ---
    contador = helpers.obtener_contador_carrito(driver)
    assert contador == 1, f"Se esperaba 1 ítem en el carrito, el badge muestra {contador}"

    # --- Acción: navegar al carrito ---
    helpers.ir_al_carrito(driver)

    # --- Validación: el producto correcto aparece en el carrito ---
    nombres_en_carrito = helpers.obtener_nombres_en_carrito(driver)

    assert len(nombres_en_carrito) == 1, (
        f"Se esperaba 1 producto en el carrito, se encontraron {len(nombres_en_carrito)}"
    )
    assert producto_agregado["nombre"] in nombres_en_carrito, (
        f"El producto '{producto_agregado['nombre']}' no aparece en el carrito. "
        f"Contenido actual: {nombres_en_carrito}"
    )
