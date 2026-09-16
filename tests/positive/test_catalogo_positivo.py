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
