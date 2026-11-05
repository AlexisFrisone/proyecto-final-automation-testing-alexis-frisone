"""
Pruebas de UI: agregar y quitar productos del carrito.

Las combinaciones de productos se leen de data/productos.json.
"""

import pytest

from pages.base_page import convertir_precio
from utils.data_loader import como_parametros, leer_json

pytestmark = [pytest.mark.ui, pytest.mark.carrito]

COMBINACIONES = leer_json("productos.json")["combinaciones_carrito"]


@pytest.mark.smoke
@pytest.mark.parametrize("combinacion", como_parametros(COMBINACIONES))
def test_agregar_productos_los_lista_en_el_carrito(inventario, combinacion):
    """Los productos agregados actualizan el badge y aparecen en el carrito con su precio."""
    agregados = [inventario.agregar_por_nombre(nombre) for nombre in combinacion["productos"]]

    cantidad = len(agregados)
    assert inventario.cantidad_en_carrito() == cantidad, (
        f"El badge debería mostrar {cantidad}, muestra {inventario.cantidad_en_carrito()}"
    )
    for nombre in combinacion["productos"]:
        assert inventario.texto_boton(nombre) == "Remove", (
            f"El botón de '{nombre}' no cambió a 'Remove'"
        )

    carrito = inventario.ir_al_carrito()
    assert sorted(carrito.nombres()) == sorted(combinacion["productos"]), (
        f"El carrito contiene {carrito.nombres()}, se esperaba {combinacion['productos']}"
    )
    precios_catalogo = sorted(convertir_precio(p["precio"]) for p in agregados)
    assert sorted(carrito.precios()) == precios_catalogo, (
        "Los precios del carrito no coinciden con los del catálogo"
    )


def test_agregar_desde_el_detalle_del_producto(inventario):
    """Agregar desde el detalle actualiza el badge, el catálogo y el carrito."""
    datos, detalle = inventario.abrir_detalle(indice=1)
    detalle.agregar_al_carrito()

    assert detalle.texto_boton_quitar() == "Remove"
    assert detalle.cantidad_en_carrito() == 1

    catalogo = detalle.volver_al_catalogo()
    assert catalogo.texto_boton(datos["nombre"]) == "Remove", (
        "El catálogo no refleja que el producto ya está en el carrito"
    )
    assert catalogo.ir_al_carrito().nombres() == [datos["nombre"]]


def test_quitar_el_unico_producto_hace_desaparecer_el_badge(inventario):
    """Al vaciar el carrito, SauceDemo elimina el badge en lugar de mostrar 0."""
    assert not inventario.hay_badge_carrito(), "No debería haber badge con el carrito vacío"

    inventario.agregar_por_indice(0)
    assert inventario.cantidad_en_carrito() == 1

    inventario.quitar_por_indice(0)
    assert not inventario.hay_badge_carrito(), "El badge sigue presente con el carrito vacío"
    assert inventario.ir_al_carrito().nombres() == [], "El carrito debería estar vacío"


def test_quitar_un_producto_desde_el_carrito(inventario):
    """Quitar un ítem en el carrito lo saca de la lista y actualiza el badge."""
    quitado = inventario.agregar_por_indice(0)
    conservado = inventario.agregar_por_indice(1)
    carrito = inventario.ir_al_carrito()

    carrito.quitar_por_indice(0)

    assert carrito.nombres() == [conservado["nombre"]], (
        f"'{quitado['nombre']}' debería haberse quitado del carrito"
    )
    assert carrito.cantidad_en_carrito() == 1, "El badge no se actualizó al quitar el producto"


def test_agregar_todos_los_productos_del_catalogo(inventario):
    """Límite superior: todo el catálogo entra al carrito una sola vez cada producto."""
    cantidad = inventario.cantidad_productos()
    agregados = [inventario.agregar_por_indice(i)["nombre"] for i in range(cantidad)]

    assert inventario.cantidad_en_carrito() == cantidad
    assert all(texto == "Remove" for texto in inventario.textos_botones()), (
        "No todos los botones cambiaron a 'Remove'"
    )
    assert sorted(inventario.ir_al_carrito().nombres()) == sorted(agregados)


def test_el_carrito_se_conserva_al_recargar_y_al_reordenar(inventario):
    """Recargar la página o reordenar el catálogo no altera los productos agregados."""
    agregados = {inventario.agregar_por_indice(i)["nombre"] for i in (0, 1)}

    inventario.refrescar()
    assert inventario.esperar_cantidad_en_carrito(2) == 2, "El carrito cambió al recargar"

    inventario.ordenar(inventario.ORDEN_PRECIO_DESC)
    assert inventario.nombres_agregados() == agregados, (
        "Tras reordenar, el estado 'Remove' no sigue a los productos agregados"
    )
    assert set(inventario.ir_al_carrito().nombres()) == agregados


def test_reset_app_state_vacia_el_carrito(inventario):
    """La opción "Reset App State" del menú lateral vacía el carrito."""
    inventario.agregar_por_indice(0)
    inventario.agregar_por_indice(1)
    assert inventario.cantidad_en_carrito() == 2

    inventario.resetear_estado_app()

    assert inventario.cantidad_en_carrito() == 0, "El badge debería desaparecer tras el reset"
    assert inventario.ir_al_carrito().nombres() == [], "El carrito debería quedar vacío"
