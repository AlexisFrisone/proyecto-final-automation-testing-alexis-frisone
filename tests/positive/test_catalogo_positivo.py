"""
Caso positivo: navegación y verificación del catálogo de productos.

Cubre la segunda consigna obligatoria de la pre-entrega.
"""

import pytest

import helpers
from helpers import Localizadores


@pytest.mark.catalogo
@pytest.mark.smoke
def test_catalogo_muestra_productos_y_controles_de_interfaz(driver_logueado):
    """La página de inventario carga con productos y sus controles principales.

    Parte de una sesión ya iniciada (fixture `driver_logueado`), porque lo que se
    valida acá es el catálogo, no el login.

    Validaciones:
        - El título de la sección es "Products".
        - Hay al menos un producto visible.
        - El menú lateral, el filtro de ordenamiento y el ícono del carrito existen.
        - El primer producto expone nombre y precio con formato válido.
    """
    driver = driver_logueado

    # --- Validación: título de la página de inventario ---
    titulo = helpers.obtener_titulo_seccion(driver)
    assert titulo == "Products", f"Se esperaba el título 'Products', se obtuvo '{titulo}'"

    # --- Validación: presencia de productos ---
    productos = helpers.obtener_productos(driver)
    assert len(productos) > 0, "El catálogo no muestra ningún producto"

    # --- Validación: elementos importantes de la interfaz ---
    assert helpers.elemento_existe(driver, Localizadores.BOTON_MENU), (
        "El botón del menú lateral no está presente"
    )
    assert helpers.elemento_existe(driver, Localizadores.FILTRO_ORDENAMIENTO), (
        "El filtro de ordenamiento de productos no está presente"
    )
    assert helpers.elemento_existe(driver, Localizadores.ICONO_CARRITO), (
        "El ícono del carrito no está presente"
    )

    # --- Validación: datos del primer producto ---
    primer_producto = helpers.obtener_datos_producto(productos[0])

    assert primer_producto["nombre"], "El primer producto no tiene nombre visible"
    assert primer_producto["precio"].startswith("$"), (
        f"El precio no tiene el formato esperado: {primer_producto['precio']}"
    )

    # Se deja constancia en la salida de pytest (visible con la opción -s).
    print(
        f"\nPrimer producto del catálogo -> "
        f"{primer_producto['nombre']} | {primer_producto['precio']}"
    )


@pytest.mark.catalogo
def test_ordenar_por_precio_de_menor_a_mayor(driver_logueado):
    """El filtro "Price (low to high)" ordena el catálogo por precio ascendente.

    Validaciones:
        - Los precios mostrados quedan en orden ascendente.
        - No se pierde ni se agrega ningún producto al reordenar.
    """
    driver = driver_logueado
    cantidad_inicial = len(helpers.obtener_productos(driver))

    # --- Acción ---
    helpers.ordenar_productos(driver, helpers.ORDEN_PRECIO_MENOR_A_MAYOR)

    # --- Validación ---
    precios = helpers.obtener_precios_productos(driver)
    assert precios == sorted(precios), (
        f"Los precios no están ordenados de menor a mayor: {precios}"
    )
    assert len(precios) == cantidad_inicial, (
        f"Se esperaban {cantidad_inicial} productos tras ordenar, hay {len(precios)}"
    )


@pytest.mark.catalogo
def test_ordenar_por_nombre_de_z_a_a(driver_logueado):
    """El filtro "Name (Z to A)" invierte el orden alfabético del catálogo.

    Se compara contra el orden por defecto (A a Z) leído del propio catálogo, sin
    hardcodear nombres de productos.
    """
    driver = driver_logueado
    nombres_a_z = helpers.obtener_nombres_productos(driver)
    assert nombres_a_z == sorted(nombres_a_z), (
        f"El orden por defecto debería ser alfabético: {nombres_a_z}"
    )

    # --- Acción ---
    helpers.ordenar_productos(driver, helpers.ORDEN_NOMBRE_Z_A)

    # --- Validación ---
    nombres_z_a = helpers.obtener_nombres_productos(driver)
    assert nombres_z_a == list(reversed(nombres_a_z)), (
        f"El orden Z a A no es el inverso del A a Z: {nombres_z_a}"
    )


@pytest.mark.catalogo
def test_ordenar_por_precio_de_mayor_a_menor(driver_logueado):
    """El filtro "Price (high to low)" ordena el catálogo por precio descendente."""
    driver = driver_logueado

    # --- Acción ---
    helpers.ordenar_productos(driver, helpers.ORDEN_PRECIO_MAYOR_A_MENOR)

    # --- Validación ---
    precios = helpers.obtener_precios_productos(driver)
    assert precios == sorted(precios, reverse=True), (
        f"Los precios no están ordenados de mayor a menor: {precios}"
    )


@pytest.mark.catalogo
def test_detalle_de_producto_coincide_con_el_catalogo(driver_logueado):
    """La página de detalle muestra el mismo nombre y precio que la tarjeta del catálogo.

    Pasos:
        1. Hacer clic en el nombre del primer producto.
        2. Comparar nombre y precio del detalle con los del catálogo.
        3. Volver con "Back to products" y confirmar que se regresa al inventario.
    """
    driver = driver_logueado

    # --- Acción: abrir el detalle ---
    datos_catalogo = helpers.abrir_detalle_producto(driver, indice=0)
    datos_detalle = helpers.obtener_datos_detalle(driver)

    # --- Validación: datos consistentes ---
    assert datos_detalle == datos_catalogo, (
        f"El detalle muestra {datos_detalle}, pero el catálogo mostraba {datos_catalogo}"
    )

    # --- Acción y validación: volver al catálogo ---
    helpers.esperar_elemento_clickeable(
        driver, Localizadores.BOTON_VOLVER_PRODUCTOS
    ).click()
    helpers.esperar_url_contiene(driver, "/inventory.html")
    assert helpers.obtener_titulo_seccion(driver) == "Products", (
        "'Back to products' no volvió a la página de productos"
    )
