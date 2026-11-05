"""Page Object del catálogo de productos (/inventory.html)."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import PaginaConSesion, convertir_precio, data_test


class InventarioPage(PaginaConSesion):
    RUTA = "inventory.html"

    LISTA = data_test("inventory-list")
    TARJETA = data_test("inventory-item")
    NOMBRE = data_test("inventory-item-name")
    PRECIO = data_test("inventory-item-price")
    # Botón de cada tarjeta: dice "Add to cart" o "Remove" según el estado.
    BOTON_TARJETA = (By.TAG_NAME, "button")
    FILTRO_ORDEN = data_test("product-sort-container")

    # Valores del <select> de ordenamiento.
    ORDEN_NOMBRE_A_Z = "az"
    ORDEN_NOMBRE_Z_A = "za"
    ORDEN_PRECIO_ASC = "lohi"
    ORDEN_PRECIO_DESC = "hilo"

    def esperar_carga(self):
        self.esperar_url("/inventory.html")
        self.esperar_visible(self.LISTA)
        return self

    # ------------------------------------------------------------------
    # Lectura del catálogo
    # ------------------------------------------------------------------

    def _tarjetas(self):
        return self.esperar_todos(self.TARJETA)

    @classmethod
    def _datos_tarjeta(cls, tarjeta):
        return {
            "nombre": tarjeta.find_element(*cls.NOMBRE).text,
            "precio": tarjeta.find_element(*cls.PRECIO).text,
        }

    def productos(self):
        """Lista de productos visibles como diccionarios {'nombre', 'precio'}."""
        return [self._datos_tarjeta(tarjeta) for tarjeta in self._tarjetas()]

    def cantidad_productos(self):
        return len(self._tarjetas())

    def nombres(self):
        return [producto["nombre"] for producto in self.productos()]

    def precios(self):
        return [convertir_precio(producto["precio"]) for producto in self.productos()]

    def _tarjeta_por_nombre(self, nombre):
        for tarjeta in self._tarjetas():
            if tarjeta.find_element(*self.NOMBRE).text == nombre:
                return tarjeta
        raise ValueError(f"No existe el producto '{nombre}' en el catálogo")

    def texto_boton(self, nombre):
        """Texto del botón de la tarjeta: 'Add to cart' o 'Remove'."""
        return self._tarjeta_por_nombre(nombre).find_element(*self.BOTON_TARJETA).text

    def textos_botones(self):
        return [t.find_element(*self.BOTON_TARJETA).text for t in self._tarjetas()]

    def nombres_agregados(self):
        """Nombres de los productos cuyo botón figura como 'Remove'."""
        return {
            self._datos_tarjeta(t)["nombre"]
            for t in self._tarjetas()
            if t.find_element(*self.BOTON_TARJETA).text == "Remove"
        }

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def agregar_por_indice(self, indice=0):
        """Agrega el producto de la posición indicada y devuelve sus datos.

        Devolver nombre y precio permite validarlos después sin hardcodearlos.
        """
        tarjeta = self._tarjetas()[indice]
        datos = self._datos_tarjeta(tarjeta)
        self.log.info("Agregando al carrito: %s (%s)", datos["nombre"], datos["precio"])
        tarjeta.find_element(*self.BOTON_TARJETA).click()
        return datos

    def agregar_por_nombre(self, nombre):
        """Agrega el producto con ese nombre exacto y devuelve sus datos."""
        tarjeta = self._tarjeta_por_nombre(nombre)
        datos = self._datos_tarjeta(tarjeta)
        self.log.info("Agregando al carrito: %s (%s)", datos["nombre"], datos["precio"])
        tarjeta.find_element(*self.BOTON_TARJETA).click()
        return datos

    def quitar_por_indice(self, indice=0):
        """Quita el producto desde el catálogo (el mismo botón pasa a decir 'Remove')."""
        tarjeta = self._tarjetas()[indice]
        self.log.info("Quitando del carrito: %s", self._datos_tarjeta(tarjeta)["nombre"])
        tarjeta.find_element(*self.BOTON_TARJETA).click()
        return self

    def ordenar(self, criterio):
        """Elige un criterio del filtro (ver constantes ORDEN_*)."""
        self.log.info("Ordenando el catálogo por '%s'", criterio)
        Select(self.esperar_visible(self.FILTRO_ORDEN)).select_by_value(criterio)
        return self

    def abrir_detalle(self, indice=0):
        """Abre el detalle del producto haciendo clic en su nombre.

        Devuelve una tupla (datos_en_catalogo, DetalleProductoPage), para poder comparar
        lo que mostraba la tarjeta con lo que muestra el detalle.
        """
        from pages.detalle_producto_page import DetalleProductoPage

        tarjeta = self._tarjetas()[indice]
        datos = self._datos_tarjeta(tarjeta)
        self.log.info("Abriendo el detalle de %s", datos["nombre"])
        tarjeta.find_element(*self.NOMBRE).click()
        return datos, DetalleProductoPage(self.driver).esperar_carga()

    def refrescar(self):
        self.log.info("Recargando la página")
        self.driver.refresh()
        return self.esperar_carga()
