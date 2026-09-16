"""
Caso end-to-end: recorrido completo de compra.

A diferencia de los tests anteriores, que validan una funcionalidad aislada, este
caso atraviesa todas las pantallas de la aplicación en un único flujo continuo:
login, catálogo, carrito, checkout y confirmación. Su objetivo es detectar
problemas de integración entre pantallas que los tests individuales no revelan.
"""

import pytest

import helpers
from helpers import Localizadores


@pytest.mark.e2e
def test_flujo_completo_desde_login_hasta_confirmacion_de_compra(driver):
    """Un usuario compra dos productos de punta a punta.

    Recorrido:
        1. Login con credenciales válidas.
        2. Agregar dos productos del catálogo.
        3. Abrir el carrito y verificar su contenido.
        4. Completar el formulario de checkout.
        5. Revisar el resumen del pedido.
        6. Finalizar la compra y validar el mensaje de confirmación.
        7. Volver al catálogo y comprobar que el carrito quedó vacío.
    """

    # --- Paso 1: iniciar sesión ---
    helpers.login_exitoso(driver)
    assert helpers.obtener_titulo_seccion(driver) == "Products", (
        "El login no llevó a la página de productos"
    )

    # --- Paso 2: agregar dos productos al carrito ---
    primer_producto = helpers.agregar_producto_por_indice(driver, indice=0)
    segundo_producto = helpers.agregar_producto_por_indice(driver, indice=1)

    contador = helpers.obtener_contador_carrito(driver)
    assert contador == 2, f"Se esperaban 2 ítems en el carrito, el badge muestra {contador}"

    # --- Paso 3: revisar el contenido del carrito ---
    helpers.ir_al_carrito(driver)
    nombres_en_carrito = helpers.obtener_nombres_en_carrito(driver)

    assert len(nombres_en_carrito) == 2, (
        f"El carrito debería tener 2 productos, tiene {len(nombres_en_carrito)}"
    )
    assert primer_producto["nombre"] in nombres_en_carrito, (
        f"Falta '{primer_producto['nombre']}' en el carrito"
    )
    assert segundo_producto["nombre"] in nombres_en_carrito, (
        f"Falta '{segundo_producto['nombre']}' en el carrito"
    )

    # --- Paso 4: completar los datos del checkout ---
    helpers.esperar_elemento_clickeable(driver, Localizadores.BOTON_CHECKOUT).click()
    helpers.esperar_url_contiene(driver, "/checkout-step-one.html")

    helpers.completar_datos_checkout(
        driver,
        nombre=helpers.DATOS_CHECKOUT["nombre"],
        apellido=helpers.DATOS_CHECKOUT["apellido"],
        codigo_postal=helpers.DATOS_CHECKOUT["codigo_postal"],
    )

    # --- Paso 5: verificar el resumen del pedido ---
    helpers.esperar_url_contiene(driver, "/checkout-step-two.html")

    nombres_en_resumen = helpers.obtener_nombres_en_carrito(driver)
    assert sorted(nombres_en_resumen) == sorted(nombres_en_carrito), (
        "Los productos del resumen no coinciden con los del carrito"
    )

    total = helpers.esperar_elemento(driver, Localizadores.TOTAL_COMPRA).text
    assert "$" in total, f"El resumen no muestra un total válido: '{total}'"

    # --- Paso 6: finalizar la compra ---
    helpers.esperar_elemento_clickeable(driver, Localizadores.BOTON_FINALIZAR).click()
    helpers.esperar_url_contiene(driver, "/checkout-complete.html")

    confirmacion = helpers.esperar_elemento(
        driver, Localizadores.MENSAJE_COMPRA_EXITOSA
    ).text
    assert confirmacion == "Thank you for your order!", (
        f"Mensaje de confirmación inesperado: '{confirmacion}'"
    )

    # --- Paso 7: volver al catálogo con el carrito vacío ---
    helpers.esperar_elemento_clickeable(
        driver, Localizadores.BOTON_VOLVER_PRODUCTOS
    ).click()
    helpers.esperar_url_contiene(driver, "/inventory.html")

    assert helpers.obtener_contador_carrito(driver) == 0, (
        "El carrito debería quedar vacío después de completar la compra"
    )
