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


@pytest.mark.carrito
@pytest.mark.edge
def test_agregar_todos_los_productos_del_catalogo(driver_logueado):
    """Límite superior: agregar todos los productos disponibles al carrito.

    Validaciones:
        - El badge coincide con la cantidad total de productos del catálogo.
        - Todos los botones cambian a "Remove".
        - El carrito lista cada producto una sola vez.
    """
    driver = driver_logueado
    cantidad_productos = len(helpers.obtener_productos(driver))

    # --- Acción: agregar todos ---
    agregados = [
        helpers.agregar_producto_por_indice(driver, indice=i)
        for i in range(cantidad_productos)
    ]

    # --- Validación: contador y botones ---
    contador = helpers.obtener_contador_carrito(driver)
    assert contador == cantidad_productos, (
        f"Se esperaban {cantidad_productos} ítems, el badge muestra {contador}"
    )
    textos_botones = [
        boton.text for boton in driver.find_elements(*Localizadores.BOTON_AGREGAR)
    ]
    assert all(texto == "Remove" for texto in textos_botones), (
        f"No todos los botones cambiaron a 'Remove': {textos_botones}"
    )

    # --- Validación: contenido del carrito sin duplicados ---
    helpers.ir_al_carrito(driver)
    nombres_en_carrito = helpers.obtener_nombres_en_carrito(driver)
    assert sorted(nombres_en_carrito) == sorted(p["nombre"] for p in agregados), (
        f"El carrito no contiene todos los productos: {nombres_en_carrito}"
    )


@pytest.mark.carrito
@pytest.mark.edge
def test_el_carrito_se_conserva_al_recargar_la_pagina(driver_logueado):
    """Recargar el navegador no vacía el carrito.

    SauceDemo guarda el carrito en el almacenamiento local del navegador; un refresh
    (F5) es una acción común del usuario que no debería hacerle perder su compra.
    """
    driver = driver_logueado
    primero = helpers.agregar_producto_por_indice(driver, indice=0)
    segundo = helpers.agregar_producto_por_indice(driver, indice=1)

    # --- Acción: recargar la página ---
    driver.refresh()
    helpers.obtener_productos(driver)

    # --- Validación: el contador se mantiene ---
    contador = helpers.esperar_contador_carrito(driver, 2)
    assert contador == 2, f"Tras recargar se esperaban 2 ítems, el badge muestra {contador}"

    # --- Validación: los productos siguen en el carrito ---
    helpers.ir_al_carrito(driver)
    nombres_en_carrito = helpers.obtener_nombres_en_carrito(driver)
    assert sorted(nombres_en_carrito) == sorted([primero["nombre"], segundo["nombre"]]), (
        f"El carrito cambió después de recargar: {nombres_en_carrito}"
    )


@pytest.mark.carrito
@pytest.mark.edge
def test_reordenar_el_catalogo_no_altera_el_carrito(driver_logueado):
    """Cambiar el orden del catálogo no pierde ni mezcla los productos agregados.

    El reordenamiento vuelve a dibujar todas las tarjetas; el estado "Remove" debe
    seguir asociado a los mismos productos y no a las mismas posiciones.
    """
    driver = driver_logueado
    agregados = {
        helpers.agregar_producto_por_indice(driver, indice=i)["nombre"] for i in (0, 1)
    }

    # --- Acción: reordenar el catálogo ---
    helpers.ordenar_productos(driver, helpers.ORDEN_PRECIO_MAYOR_A_MENOR)

    # --- Validación: los botones "Remove" siguen en los productos agregados ---
    con_remove = {
        helpers.obtener_datos_producto(producto)["nombre"]
        for producto in helpers.obtener_productos(driver)
        if producto.find_element(*Localizadores.BOTON_AGREGAR).text == "Remove"
    }
    assert con_remove == agregados, (
        f"Tras reordenar, figuran como agregados {con_remove}, se esperaba {agregados}"
    )
    assert helpers.obtener_contador_carrito(driver) == 2, (
        "El contador cambió al reordenar el catálogo"
    )

    # --- Validación: el carrito no cambió ---
    helpers.ir_al_carrito(driver)
    assert set(helpers.obtener_nombres_en_carrito(driver)) == agregados, (
        "El contenido del carrito cambió al reordenar el catálogo"
    )


@pytest.mark.carrito
@pytest.mark.edge
def test_agregar_y_quitar_el_mismo_producto_repetidas_veces(driver_logueado):
    """Alternar "Add to cart" / "Remove" varias veces deja el carrito consistente.

    Simula a un usuario indeciso: tres ciclos de agregar y quitar, y un agregado
    final. El producto debe quedar una sola vez en el carrito.
    """
    driver = driver_logueado

    # --- Acción: tres ciclos agregar/quitar ---
    for ciclo in range(1, 4):
        helpers.agregar_producto_por_indice(driver, indice=0)
        assert helpers.obtener_contador_carrito(driver) == 1, (
            f"Ciclo {ciclo}: el badge debería mostrar 1 tras agregar"
        )
        helpers.remover_producto_por_indice(driver, indice=0)
        assert helpers.obtener_contador_carrito(driver) == 0, (
            f"Ciclo {ciclo}: el badge debería desaparecer tras quitar"
        )

    # --- Acción: agregado final ---
    producto = helpers.agregar_producto_por_indice(driver, indice=0)

    # --- Validación: una sola unidad en el carrito ---
    assert helpers.obtener_contador_carrito(driver) == 1
    helpers.ir_al_carrito(driver)
    assert helpers.obtener_nombres_en_carrito(driver) == [producto["nombre"]], (
        "El producto debería figurar una única vez en el carrito"
    )
