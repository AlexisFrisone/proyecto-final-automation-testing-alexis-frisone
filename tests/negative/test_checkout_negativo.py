"""
Casos negativos del formulario de checkout.

El checkout exige nombre, apellido y código postal. Si falta alguno, la aplicación
debe mostrar el aviso correspondiente y no avanzar al resumen del pedido.
"""

import pytest

import helpers


def _abrir_checkout_con_un_producto(driver):
    """Deja al usuario en el formulario de checkout con un producto en el carrito."""
    helpers.agregar_producto_por_indice(driver, indice=0)
    helpers.ir_al_carrito(driver)
    helpers.ir_al_checkout(driver)


def _validar_que_no_avanzo(driver):
    assert "/checkout-step-two.html" not in driver.current_url, (
        "El checkout avanzó al resumen aunque faltaban datos obligatorios"
    )


@pytest.mark.carrito
@pytest.mark.negativo
def test_checkout_sin_nombre_muestra_error(driver_logueado):
    """Sin nombre, el checkout reclama el campo "First Name"."""
    driver = driver_logueado
    _abrir_checkout_con_un_producto(driver)

    helpers.completar_datos_checkout(
        driver,
        nombre="",
        apellido=helpers.DATOS_CHECKOUT["apellido"],
        codigo_postal=helpers.DATOS_CHECKOUT["codigo_postal"],
    )

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_NOMBRE_REQUERIDO, (
        f"Se esperaba el aviso de nombre requerido, se obtuvo: '{mensaje}'"
    )
    _validar_que_no_avanzo(driver)


@pytest.mark.carrito
@pytest.mark.negativo
def test_checkout_sin_apellido_muestra_error(driver_logueado):
    """Sin apellido, el checkout reclama el campo "Last Name"."""
    driver = driver_logueado
    _abrir_checkout_con_un_producto(driver)

    helpers.completar_datos_checkout(
        driver,
        nombre=helpers.DATOS_CHECKOUT["nombre"],
        apellido="",
        codigo_postal=helpers.DATOS_CHECKOUT["codigo_postal"],
    )

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_APELLIDO_REQUERIDO, (
        f"Se esperaba el aviso de apellido requerido, se obtuvo: '{mensaje}'"
    )
    _validar_que_no_avanzo(driver)


@pytest.mark.carrito
@pytest.mark.negativo
def test_checkout_sin_codigo_postal_muestra_error(driver_logueado):
    """Sin código postal, el checkout reclama el campo "Postal Code"."""
    driver = driver_logueado
    _abrir_checkout_con_un_producto(driver)

    helpers.completar_datos_checkout(
        driver,
        nombre=helpers.DATOS_CHECKOUT["nombre"],
        apellido=helpers.DATOS_CHECKOUT["apellido"],
        codigo_postal="",
    )

    mensaje = helpers.obtener_mensaje_error(driver)
    assert mensaje == helpers.ERROR_CODIGO_POSTAL_REQUERIDO, (
        f"Se esperaba el aviso de código postal requerido, se obtuvo: '{mensaje}'"
    )
    _validar_que_no_avanzo(driver)
