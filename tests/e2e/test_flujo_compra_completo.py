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


def _completar_datos_validos(driver):
    """Carga los datos de checkout de prueba y espera el resumen del pedido."""
    helpers.completar_datos_checkout(
        driver,
        nombre=helpers.DATOS_CHECKOUT["nombre"],
        apellido=helpers.DATOS_CHECKOUT["apellido"],
        codigo_postal=helpers.DATOS_CHECKOUT["codigo_postal"],
    )
    helpers.esperar_url_contiene(driver, "/checkout-step-two.html")


def _validar_confirmacion(driver):
    confirmacion = helpers.esperar_elemento(
        driver, Localizadores.MENSAJE_COMPRA_EXITOSA
    ).text
    assert confirmacion == "Thank you for your order!", (
        f"Mensaje de confirmación inesperado: '{confirmacion}'"
    )


@pytest.mark.e2e
def test_el_resumen_calcula_subtotal_impuestos_y_total_correctamente(driver):
    """Los importes del resumen son consistentes con los precios del catálogo.

    Validaciones:
        - Subtotal = suma de los precios de los productos agregados.
        - Total = subtotal + impuestos.
    """
    helpers.login_exitoso(driver)
    agregados = [helpers.agregar_producto_por_indice(driver, indice=i) for i in (0, 2)]
    suma_esperada = sum(helpers.convertir_precio(p["precio"]) for p in agregados)

    helpers.ir_al_carrito(driver)
    helpers.ir_al_checkout(driver)
    _completar_datos_validos(driver)

    # --- Validación: importes del resumen ---
    subtotal = helpers.convertir_precio(
        helpers.esperar_elemento(driver, Localizadores.SUBTOTAL_COMPRA).text
    )
    impuesto = helpers.convertir_precio(
        helpers.esperar_elemento(driver, Localizadores.IMPUESTO_COMPRA).text
    )
    total = helpers.convertir_precio(
        helpers.esperar_elemento(driver, Localizadores.TOTAL_COMPRA).text
    )

    assert subtotal == pytest.approx(suma_esperada), (
        f"El subtotal ({subtotal}) no coincide con la suma de precios ({suma_esperada})"
    )
    assert impuesto > 0, f"El impuesto debería ser positivo, se obtuvo {impuesto}"
    assert total == pytest.approx(subtotal + impuesto), (
        f"El total ({total}) no es subtotal ({subtotal}) + impuesto ({impuesto})"
    )

    helpers.finalizar_compra(driver)
    _validar_confirmacion(driver)


@pytest.mark.e2e
def test_cancelar_en_el_resumen_conserva_el_carrito_y_permite_comprar(driver):
    """Cancelar en el resumen vuelve al catálogo sin perder el carrito.

    Recorrido:
        1. Login, agregar un producto y llegar al resumen del pedido.
        2. Cancelar: se vuelve al inventario con el producto todavía en el carrito.
        3. Retomar el checkout y completar la compra.
    """
    helpers.login_exitoso(driver)
    producto = helpers.agregar_producto_por_indice(driver, indice=0)
    helpers.ir_al_carrito(driver)
    helpers.ir_al_checkout(driver)
    _completar_datos_validos(driver)

    # --- Acción: cancelar desde el resumen ---
    helpers.esperar_elemento_clickeable(driver, Localizadores.BOTON_CANCELAR).click()
    helpers.esperar_url_contiene(driver, "/inventory.html")

    assert helpers.obtener_contador_carrito(driver) == 1, (
        "Cancelar el checkout no debería vaciar el carrito"
    )

    # --- Acción: retomar y finalizar ---
    helpers.ir_al_carrito(driver)
    assert helpers.obtener_nombres_en_carrito(driver) == [producto["nombre"]], (
        "El carrito cambió después de cancelar el checkout"
    )
    helpers.ir_al_checkout(driver)
    _completar_datos_validos(driver)
    helpers.finalizar_compra(driver)
    _validar_confirmacion(driver)


@pytest.mark.e2e
def test_seguir_comprando_desde_el_carrito_y_finalizar_la_compra(driver):
    """El botón "Continue Shopping" permite sumar productos antes de pagar.

    Recorrido:
        1. Login, agregar un producto y abrir el carrito.
        2. Volver al catálogo con "Continue Shopping" y agregar otro producto.
        3. Verificar que el carrito y el resumen contienen ambos productos.
        4. Finalizar la compra.
    """
    helpers.login_exitoso(driver)
    primero = helpers.agregar_producto_por_indice(driver, indice=0)
    helpers.ir_al_carrito(driver)

    # --- Acción: seguir comprando ---
    helpers.esperar_elemento_clickeable(
        driver, Localizadores.BOTON_SEGUIR_COMPRANDO
    ).click()
    helpers.esperar_url_contiene(driver, "/inventory.html")
    segundo = helpers.agregar_producto_por_indice(driver, indice=3)

    # --- Validación: el carrito tiene ambos productos ---
    helpers.ir_al_carrito(driver)
    esperados = sorted([primero["nombre"], segundo["nombre"]])
    assert sorted(helpers.obtener_nombres_en_carrito(driver)) == esperados, (
        "El carrito no contiene los dos productos agregados"
    )

    helpers.ir_al_checkout(driver)
    _completar_datos_validos(driver)
    assert sorted(helpers.obtener_nombres_en_carrito(driver)) == esperados, (
        "El resumen no contiene los dos productos agregados"
    )

    helpers.finalizar_compra(driver)
    _validar_confirmacion(driver)


@pytest.mark.e2e
def test_quitar_un_producto_desde_el_carrito_antes_de_comprar(driver):
    """Un producto quitado en el carrito no llega al resumen ni se cobra.

    Recorrido:
        1. Login y agregar dos productos.
        2. En el carrito, quitar el primero.
        3. El resumen muestra solo el restante y el subtotal es su precio.
        4. Finalizar la compra.
    """
    helpers.login_exitoso(driver)
    quitado = helpers.agregar_producto_por_indice(driver, indice=0)
    conservado = helpers.agregar_producto_por_indice(driver, indice=1)
    helpers.ir_al_carrito(driver)

    # --- Acción: quitar el primer producto del carrito ---
    helpers.quitar_producto_del_carrito(driver, indice=0)

    assert helpers.obtener_nombres_en_carrito(driver) == [conservado["nombre"]], (
        f"'{quitado['nombre']}' debería haberse quitado del carrito"
    )
    assert helpers.obtener_contador_carrito(driver) == 1, (
        "El badge no se actualizó al quitar el producto"
    )

    # --- Validación: el resumen refleja el cambio ---
    helpers.ir_al_checkout(driver)
    _completar_datos_validos(driver)
    assert helpers.obtener_nombres_en_carrito(driver) == [conservado["nombre"]], (
        "El resumen incluye productos que se quitaron del carrito"
    )
    subtotal = helpers.convertir_precio(
        helpers.esperar_elemento(driver, Localizadores.SUBTOTAL_COMPRA).text
    )
    assert subtotal == pytest.approx(helpers.convertir_precio(conservado["precio"])), (
        f"El subtotal ({subtotal}) no coincide con el precio de '{conservado['nombre']}'"
    )

    helpers.finalizar_compra(driver)
    _validar_confirmacion(driver)


@pytest.mark.e2e
def test_comprar_un_producto_desde_su_pagina_de_detalle(driver):
    """Compra completa iniciada desde la página de detalle de un producto.

    Recorrido:
        1. Login y abrir el detalle del tercer producto.
        2. Agregarlo desde el detalle e ir al carrito.
        3. Checkout: el resumen muestra ese producto con su precio como subtotal.
        4. Finalizar la compra.
    """
    helpers.login_exitoso(driver)
    producto = helpers.abrir_detalle_producto(driver, indice=2)
    helpers.esperar_elemento_clickeable(driver, Localizadores.BOTON_AGREGAR_DETALLE).click()
    helpers.esperar_elemento(driver, Localizadores.BOTON_QUITAR_DETALLE)

    helpers.ir_al_carrito(driver)
    assert helpers.obtener_nombres_en_carrito(driver) == [producto["nombre"]], (
        "El carrito no contiene el producto agregado desde el detalle"
    )

    helpers.ir_al_checkout(driver)
    _completar_datos_validos(driver)
    subtotal = helpers.convertir_precio(
        helpers.esperar_elemento(driver, Localizadores.SUBTOTAL_COMPRA).text
    )
    assert subtotal == pytest.approx(helpers.convertir_precio(producto["precio"])), (
        f"El subtotal ({subtotal}) no coincide con el precio ({producto['precio']})"
    )

    helpers.finalizar_compra(driver)
    _validar_confirmacion(driver)


@pytest.mark.e2e
def test_ordenar_por_precio_y_comprar_el_producto_mas_barato(driver):
    """Ordenar por precio ascendente, comprar el primero y pagar el mínimo del catálogo.

    Conecta el filtro del catálogo con el checkout: el producto que queda primero
    debe ser efectivamente el más barato y ese debe ser el importe cobrado.
    """
    helpers.login_exitoso(driver)
    precio_minimo = min(helpers.obtener_precios_productos(driver))

    # --- Acción: ordenar y agregar el primero ---
    helpers.ordenar_productos(driver, helpers.ORDEN_PRECIO_MENOR_A_MAYOR)
    producto = helpers.agregar_producto_por_indice(driver, indice=0)
    assert helpers.convertir_precio(producto["precio"]) == pytest.approx(precio_minimo), (
        f"El primer producto ({producto['precio']}) no es el más barato ({precio_minimo})"
    )

    # --- Checkout ---
    helpers.ir_al_carrito(driver)
    helpers.ir_al_checkout(driver)
    _completar_datos_validos(driver)
    subtotal = helpers.convertir_precio(
        helpers.esperar_elemento(driver, Localizadores.SUBTOTAL_COMPRA).text
    )
    assert subtotal == pytest.approx(precio_minimo), (
        f"El subtotal ({subtotal}) no es el precio mínimo del catálogo ({precio_minimo})"
    )

    helpers.finalizar_compra(driver)
    _validar_confirmacion(driver)


@pytest.mark.e2e
def test_dos_compras_consecutivas_en_la_misma_sesion(driver):
    """Después de una compra se puede hacer otra sin volver a iniciar sesión.

    Valida que el final de la primera compra deje la aplicación en un estado limpio:
    carrito vacío, botones en "Add to cart" y checkout funcionando otra vez.
    """
    helpers.login_exitoso(driver)

    for numero_compra, indice in ((1, 0), (2, 4)):
        producto = helpers.agregar_producto_por_indice(driver, indice=indice)
        helpers.ir_al_carrito(driver)
        assert helpers.obtener_nombres_en_carrito(driver) == [producto["nombre"]], (
            f"Compra {numero_compra}: el carrito no contiene solo '{producto['nombre']}'"
        )
        helpers.ir_al_checkout(driver)
        _completar_datos_validos(driver)
        helpers.finalizar_compra(driver)
        _validar_confirmacion(driver)

        # --- Volver al catálogo con el estado limpio ---
        helpers.esperar_elemento_clickeable(
            driver, Localizadores.BOTON_VOLVER_PRODUCTOS
        ).click()
        helpers.esperar_url_contiene(driver, "/inventory.html")
        assert helpers.obtener_contador_carrito(driver) == 0, (
            f"Compra {numero_compra}: el carrito no quedó vacío"
        )
        textos_botones = [
            boton.text for boton in driver.find_elements(*Localizadores.BOTON_AGREGAR)
        ]
        assert all(texto == "Add to cart" for texto in textos_botones), (
            f"Compra {numero_compra}: quedaron botones en 'Remove': {textos_botones}"
        )


@pytest.mark.e2e
def test_el_carrito_se_conserva_tras_cerrar_sesion_y_se_completa_la_compra(driver):
    """El carrito sobrevive a un logout/login y la compra se retoma sin perder nada.

    SauceDemo guarda el carrito en el navegador, así que un usuario que cierra sesión
    a mitad de la compra lo encuentra intacto al volver.

    Recorrido:
        1. Login y agregar dos productos.
        2. Logout y nuevo login.
        3. El carrito conserva los dos productos.
        4. Completar la compra con ambos.
    """
    helpers.login_exitoso(driver)
    agregados = sorted(
        helpers.agregar_producto_por_indice(driver, indice=i)["nombre"] for i in (0, 1)
    )
    assert helpers.obtener_contador_carrito(driver) == 2

    # --- Acción: salir y volver a entrar ---
    helpers.cerrar_sesion(driver)
    helpers.login_exitoso(driver)

    assert helpers.esperar_contador_carrito(driver, 2) == 2, (
        "El carrito debería conservar los 2 productos después de volver a iniciar sesión"
    )

    # --- Retomar la compra ---
    helpers.ir_al_carrito(driver)
    assert sorted(helpers.obtener_nombres_en_carrito(driver)) == agregados, (
        "El carrito cambió después de cerrar sesión y volver a entrar"
    )
    helpers.ir_al_checkout(driver)
    _completar_datos_validos(driver)
    assert sorted(helpers.obtener_nombres_en_carrito(driver)) == agregados, (
        "El resumen no contiene los productos conservados"
    )
    helpers.finalizar_compra(driver)
    _validar_confirmacion(driver)
