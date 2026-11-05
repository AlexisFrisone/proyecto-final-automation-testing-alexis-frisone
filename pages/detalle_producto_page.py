"""Page Object del detalle de un producto (/inventory-item.html?id=N)."""

from pages.base_page import PaginaConSesion, data_test


class DetalleProductoPage(PaginaConSesion):
    NOMBRE = data_test("inventory-item-name")
    PRECIO = data_test("inventory-item-price")
    BOTON_AGREGAR = data_test("add-to-cart")
    BOTON_QUITAR = data_test("remove")
    BOTON_VOLVER = data_test("back-to-products")

    def esperar_carga(self):
        self.esperar_url("/inventory-item.html")
        self.esperar_visible(self.NOMBRE)
        return self

    def datos(self):
        return {"nombre": self.texto(self.NOMBRE), "precio": self.texto(self.PRECIO)}

    def agregar_al_carrito(self):
        """Presiona "Add to cart" y espera a que el botón cambie a "Remove"."""
        self.log.info("Agregando al carrito desde el detalle")
        self.click(self.BOTON_AGREGAR)
        self.esperar_visible(self.BOTON_QUITAR)
        return self

    def texto_boton_quitar(self):
        return self.texto(self.BOTON_QUITAR)

    def volver_al_catalogo(self):
        from pages.inventario_page import InventarioPage

        self.click(self.BOTON_VOLVER)
        return InventarioPage(self.driver).esperar_carga()
