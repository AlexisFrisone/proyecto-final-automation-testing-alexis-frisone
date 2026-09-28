"""
Caso positivo: interacción con productos y carrito de compras.

Cubre la tercera consigna obligatoria de la pre-entrega.
"""

import pytest

import helpers
from helpers import Localizadores


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


@pytest.mark.carrito
def test_agregar_varios_productos_los_lista_todos_en_el_carrito(driver_logueado):
    """Agregar tres productos distintos los suma al contador y al carrito.

    Validaciones:
        - El badge muestra 3.
        - El carrito lista exactamente los tres productos agregados.
        - Los precios del carrito coinciden con los del catálogo.
    """
    driver = driver_logueado

    # --- Acción: agregar tres productos ---
    agregados = [
        helpers.agregar_producto_por_indice(driver, indice=i) for i in range(3)
    ]

    # --- Validación: contador ---
    contador = helpers.obtener_contador_carrito(driver)
    assert contador == 3, f"Se esperaban 3 ítems en el carrito, el badge muestra {contador}"

    # --- Validación: contenido del carrito ---
    helpers.ir_al_carrito(driver)
    nombres_en_carrito = helpers.obtener_nombres_en_carrito(driver)
    nombres_agregados = [producto["nombre"] for producto in agregados]
    assert sorted(nombres_en_carrito) == sorted(nombres_agregados), (
        f"El carrito contiene {nombres_en_carrito}, se esperaba {nombres_agregados}"
    )

    precios_agregados = [helpers.convertir_precio(p["precio"]) for p in agregados]
    precios_en_carrito = helpers.obtener_precios_en_carrito(driver)
    assert sorted(precios_en_carrito) == sorted(precios_agregados), (
        f"Los precios del carrito {precios_en_carrito} no coinciden con los del "
        f"catálogo {precios_agregados}"
    )


@pytest.mark.carrito
def test_agregar_producto_desde_su_pagina_de_detalle(driver_logueado):
    """El botón "Add to cart" del detalle agrega el producto igual que el catálogo.

    Validaciones:
        - El botón del detalle cambia a "Remove" y el badge muestra 1.
        - Al volver al catálogo, el producto figura como agregado.
        - El carrito contiene ese producto.
    """
    driver = driver_logueado
    producto = helpers.abrir_detalle_producto(driver, indice=1)

    # --- Acción: agregar desde el detalle ---
    helpers.esperar_elemento_clickeable(driver, Localizadores.BOTON_AGREGAR_DETALLE).click()

    # --- Validación: estado en el detalle ---
    boton_quitar = helpers.esperar_elemento(driver, Localizadores.BOTON_QUITAR_DETALLE)
    assert boton_quitar.text == "Remove", (
        f"El botón debería decir 'Remove', dice '{boton_quitar.text}'"
    )
    assert helpers.obtener_contador_carrito(driver) == 1, (
        "El badge debería mostrar 1 después de agregar desde el detalle"
    )

    # --- Validación: estado en el catálogo ---
    helpers.esperar_elemento_clickeable(
        driver, Localizadores.BOTON_VOLVER_PRODUCTOS
    ).click()
    helpers.esperar_url_contiene(driver, "/inventory.html")
    boton_catalogo = helpers.obtener_productos(driver)[1].find_element(
        *Localizadores.BOTON_AGREGAR
    )
    assert boton_catalogo.text == "Remove", (
        "El catálogo no refleja que el producto ya está en el carrito"
    )

    # --- Validación: contenido del carrito ---
    helpers.ir_al_carrito(driver)
    assert helpers.obtener_nombres_en_carrito(driver) == [producto["nombre"]], (
        f"El carrito debería contener solo '{producto['nombre']}'"
    )


@pytest.mark.carrito
def test_reset_app_state_vacia_el_carrito(driver_logueado):
    """La opción "Reset App State" del menú lateral vacía el carrito.

    Nota: SauceDemo no actualiza los botones del catálogo tras el reset (siguen
    diciendo "Remove" hasta recargar), por eso se valida el contador y el carrito.
    """
    driver = driver_logueado
    helpers.agregar_producto_por_indice(driver, indice=0)
    helpers.agregar_producto_por_indice(driver, indice=1)
    assert helpers.obtener_contador_carrito(driver) == 2

    # --- Acción ---
    helpers.resetear_estado_app(driver)

    # --- Validación ---
    assert helpers.obtener_contador_carrito(driver) == 0, (
        "El badge debería desaparecer después del reset"
    )
    driver.get(helpers.URL_CARRITO)
    helpers.esperar_elemento(driver, Localizadores.BOTON_SEGUIR_COMPRANDO)
    assert helpers.obtener_nombres_en_carrito(driver) == [], (
        "El carrito debería quedar vacío después del reset"
    )
