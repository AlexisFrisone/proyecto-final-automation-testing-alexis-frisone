"""Page Object del carrito de compras (/cart.html)."""

from selenium.webdriver.common.by import By

from pages.base_page import PaginaConSesion, convertir_precio, data_test


class ListaDeItems:
    """Lectura de la lista de productos, compartida por el carrito y el resumen del checkout.

    Ambas pantallas muestran los ítems con la misma estructura (`cart-list`).
    """

    LISTA = data_test("cart-list")
    ITEM = data_test("inventory-item")
    NOMBRE_ITEM = data_test("inventory-item-name")
    PRECIO_ITEM = data_test("inventory-item-price")

    def nombres_en_lista(self):
        """Nombres de los productos listados.

        Primero espera a que la lista esté dibujada: justo después de navegar, la URL
        ya cambió pero React todavía no renderizó los ítems y se leería una lista vacía.
        """
        self.esperar_visible(self.LISTA)
        return [e.text for e in self.driver.find_elements(*self.NOMBRE_ITEM)]

    def precios_en_lista(self):
        self.esperar_visible(self.LISTA)
        return [convertir_precio(e.text) for e in self.driver.find_elements(*self.PRECIO_ITEM)]


class CarritoPage(ListaDeItems, PaginaConSesion):
    RUTA = "cart.html"

    BOTON_QUITAR_ITEM = (By.CSS_SELECTOR, '[data-test="inventory-item"] button')
    BOTON_CHECKOUT = data_test("checkout")
    BOTON_SEGUIR_COMPRANDO = data_test("continue-shopping")

    def esperar_carga(self):
        self.esperar_url("/cart.html")
        self.esperar_visible(self.BOTON_SEGUIR_COMPRANDO)
        return self

    def abrir(self):
        super().abrir()
        return self.esperar_carga()

    def nombres(self):
        return self.nombres_en_lista()

    def precios(self):
        return self.precios_en_lista()

    def quitar_por_indice(self, indice=0):
        """Presiona "Remove" sobre el ítem indicado."""
        cantidad_antes = len(self.nombres())
        self.log.info("Quitando el ítem %d del carrito", indice)
        self.esperar_todos(self.BOTON_QUITAR_ITEM)[indice].click()
        self.esperar_que(lambda _: len(self.nombres()) == cantidad_antes - 1)
        return self

    def ir_al_checkout(self):
        from pages.checkout_page import CheckoutInformacionPage

        self.log.info("Iniciando el checkout")
        self.click(self.BOTON_CHECKOUT)
        return CheckoutInformacionPage(self.driver).esperar_carga()

    def seguir_comprando(self):
        from pages.inventario_page import InventarioPage

        self.click(self.BOTON_SEGUIR_COMPRANDO)
        return InventarioPage(self.driver).esperar_carga()
