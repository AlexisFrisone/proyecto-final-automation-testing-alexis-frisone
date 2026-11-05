"""
Pruebas de UI: navegación por el catálogo de productos.

Los criterios de ordenamiento se leen de data/productos.json.
"""

import pytest

from utils.data_loader import como_parametros, leer_json

pytestmark = [pytest.mark.ui, pytest.mark.inventario]

DATOS_PRODUCTOS = leer_json("productos.json")


@pytest.mark.smoke
def test_catalogo_muestra_todos_los_productos_con_nombre_y_precio(inventario):
    """El catálogo carga la cantidad esperada de productos, cada uno con nombre y precio."""
    productos = inventario.productos()

    assert inventario.titulo() == "Products"
    assert len(productos) == DATOS_PRODUCTOS["total_catalogo"], (
        f"Se esperaban {DATOS_PRODUCTOS['total_catalogo']} productos, hay {len(productos)}"
    )
    for producto in productos:
        assert producto["nombre"], f"Hay un producto sin nombre: {producto}"
        assert producto["precio"].startswith("$"), f"Precio con formato inválido: {producto}"
    assert inventario.cantidad_en_carrito() == 0, "El carrito debería arrancar vacío"


@pytest.mark.parametrize("orden", como_parametros(DATOS_PRODUCTOS["ordenamientos"]))
def test_ordenar_el_catalogo(inventario, orden):
    """Cada opción del filtro ordena el catálogo por el campo y sentido indicados."""
    cantidad_inicial = inventario.cantidad_productos()

    inventario.ordenar(orden["criterio"])

    valores = inventario.nombres() if orden["campo"] == "nombre" else inventario.precios()
    esperado = sorted(valores, reverse=orden["descendente"])
    assert valores == esperado, f"El catálogo no quedó ordenado por '{orden['caso']}': {valores}"
    assert len(valores) == cantidad_inicial, "Ordenar el catálogo agregó o quitó productos"


def test_detalle_de_producto_coincide_con_el_catalogo(inventario):
    """El detalle muestra el mismo nombre y precio que la tarjeta y permite volver."""
    datos_catalogo, detalle = inventario.abrir_detalle(indice=0)

    assert detalle.datos() == datos_catalogo, (
        f"El detalle muestra {detalle.datos()}, el catálogo mostraba {datos_catalogo}"
    )

    catalogo = detalle.volver_al_catalogo()
    assert catalogo.titulo() == "Products", "'Back to products' no volvió al catálogo"
