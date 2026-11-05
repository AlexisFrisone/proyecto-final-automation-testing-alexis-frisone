"""
Page Objects de las tres pantallas del checkout:

1. CheckoutInformacionPage (/checkout-step-one.html): datos del comprador.
2. CheckoutResumenPage     (/checkout-step-two.html): resumen e importes.
3. CheckoutCompletoPage    (/checkout-complete.html): confirmación de la compra.
"""

from pages.base_page import PaginaConSesion, convertir_precio, data_test
from pages.carrito_page import ListaDeItems


class CheckoutInformacionPage(PaginaConSesion):
    CAMPO_NOMBRE = data_test("firstName")
    CAMPO_APELLIDO = data_test("lastName")
    CAMPO_CODIGO_POSTAL = data_test("postalCode")
    BOTON_CONTINUAR = data_test("continue")
    BOTON_CANCELAR = data_test("cancel")
    MENSAJE_ERROR = data_test("error")

    def esperar_carga(self):
        self.esperar_url("/checkout-step-one.html")
        self.esperar_visible(self.CAMPO_NOMBRE)
        return self

    def completar_datos(self, nombre, apellido, codigo_postal):
        """Llena el formulario y presiona "Continue", sin validar el resultado."""
        self.log.info(
            "Completando datos del comprador: %r %r (CP %r)", nombre, apellido, codigo_postal
        )
        self.escribir(self.CAMPO_NOMBRE, nombre)
        self.escribir(self.CAMPO_APELLIDO, apellido)
        self.escribir(self.CAMPO_CODIGO_POSTAL, codigo_postal)
        self.click(self.BOTON_CONTINUAR)
        return self

    def continuar_con_datos(self, nombre, apellido, codigo_postal):
        """Completa datos válidos y devuelve el resumen ya cargado."""
        self.completar_datos(nombre, apellido, codigo_postal)
        return CheckoutResumenPage(self.driver).esperar_carga()

    def mensaje_error(self):
        return self.texto(self.MENSAJE_ERROR)

    def hay_error(self):
        return self.existe(self.MENSAJE_ERROR)


class CheckoutResumenPage(ListaDeItems, PaginaConSesion):
    SUBTOTAL = data_test("subtotal-label")
    IMPUESTO = data_test("tax-label")
    TOTAL = data_test("total-label")
    BOTON_FINALIZAR = data_test("finish")
    BOTON_CANCELAR = data_test("cancel")

    def esperar_carga(self):
        self.esperar_url("/checkout-step-two.html")
        self.esperar_visible(self.BOTON_FINALIZAR)
        return self

    def nombres(self):
        return self.nombres_en_lista()

    def subtotal(self):
        return convertir_precio(self.texto(self.SUBTOTAL))

    def impuesto(self):
        return convertir_precio(self.texto(self.IMPUESTO))

    def total(self):
        return convertir_precio(self.texto(self.TOTAL))

    def finalizar(self):
        self.log.info("Finalizando la compra")
        self.click(self.BOTON_FINALIZAR)
        return CheckoutCompletoPage(self.driver).esperar_carga()

    def cancelar(self):
        """Cancela desde el resumen; la app vuelve al catálogo conservando el carrito."""
        from pages.inventario_page import InventarioPage

        self.log.info("Cancelando el checkout desde el resumen")
        self.click(self.BOTON_CANCELAR)
        return InventarioPage(self.driver).esperar_carga()


class CheckoutCompletoPage(PaginaConSesion):
    MENSAJE_CONFIRMACION = data_test("complete-header")
    BOTON_VOLVER = data_test("back-to-products")

    MENSAJE_ESPERADO = "Thank you for your order!"

    def esperar_carga(self):
        self.esperar_url("/checkout-complete.html")
        self.esperar_visible(self.MENSAJE_CONFIRMACION)
        return self

    def mensaje_confirmacion(self):
        return self.texto(self.MENSAJE_CONFIRMACION)

    def volver_al_catalogo(self):
        from pages.inventario_page import InventarioPage

        self.click(self.BOTON_VOLVER)
        return InventarioPage(self.driver).esperar_carga()
