"""
base_page.py
============
Clases base de las que heredan todos los Page Objects.

- `BasePage`: esperas explícitas y acciones genéricas (clic, escribir, leer texto).
  Todas las esperas usan `WebDriverWait` + `expected_conditions`; nunca `time.sleep()`,
  para que el test avance apenas la página está lista.
- `PaginaConSesion`: agrega la barra superior y el menú lateral, que comparten todas
  las pantallas a las que sólo se accede con la sesión iniciada.
"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import TIMEOUT_UI, URL_UI
from utils.logger import obtener_logger


def data_test(valor):
    """Arma un localizador CSS para el atributo `data-test` que expone SauceDemo.

    Se priorizan estos atributos porque existen específicamente para automatizar y
    no cambian cuando se rediseña la parte visual del sitio.
    """
    return (By.CSS_SELECTOR, f'[data-test="{valor}"]')


def convertir_precio(texto):
    """Convierte un texto con importe ('$29.99' o 'Total: $43.18') a float."""
    return float(texto.split("$")[-1])


class BasePage:
    """Comportamiento común a todas las páginas."""

    # Ruta relativa de la página (por ejemplo 'cart.html'); la define cada subclase.
    RUTA = ""

    def __init__(self, driver, timeout=TIMEOUT_UI):
        self.driver = driver
        self.timeout = timeout
        self.log = obtener_logger(f"pages.{type(self).__name__}")

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def abrir(self):
        """Navega directamente a la URL de la página."""
        url = URL_UI + self.RUTA
        self.log.info("Abriendo %s", url)
        self.driver.get(url)
        return self

    @property
    def url_actual(self):
        return self.driver.current_url

    def esperar_url(self, fragmento):
        """Espera a que la URL contenga el fragmento indicado."""
        self._esperar(EC.url_contains(fragmento))

    # ------------------------------------------------------------------
    # Esperas explícitas
    # ------------------------------------------------------------------

    def _esperar(self, condicion, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(condicion)

    def esperar_visible(self, localizador):
        """Espera a que el elemento sea visible y lo devuelve."""
        return self._esperar(EC.visibility_of_element_located(localizador))

    def esperar_clickeable(self, localizador):
        """Espera a que el elemento esté visible y habilitado para recibir clics."""
        return self._esperar(EC.element_to_be_clickable(localizador))

    def esperar_todos(self, localizador):
        """Espera a que exista al menos un elemento con ese localizador y devuelve la lista."""
        self._esperar(EC.presence_of_all_elements_located(localizador))
        return self.driver.find_elements(*localizador)

    def esperar_invisible(self, localizador):
        """Espera a que el elemento deje de verse (o desaparezca del DOM)."""
        return self._esperar(EC.invisibility_of_element_located(localizador))

    def esperar_que(self, condicion, timeout=None):
        """Espera hasta que `condicion(driver)` sea verdadera; devuelve False si no ocurre.

        No lanza excepción para que el assert del test muestre el valor real.
        """
        try:
            self._esperar(condicion, timeout)
            return True
        except TimeoutException:
            return False

    def existe(self, localizador):
        """Indica si el elemento está en el DOM, sin esperar ni lanzar excepción."""
        return len(self.driver.find_elements(*localizador)) > 0

    # ------------------------------------------------------------------
    # Acciones genéricas
    # ------------------------------------------------------------------

    def click(self, localizador):
        self.esperar_clickeable(localizador).click()

    def escribir(self, localizador, texto):
        """Limpia el campo y escribe el texto indicado."""
        campo = self.esperar_visible(localizador)
        campo.clear()
        campo.send_keys(texto)

    def texto(self, localizador):
        return self.esperar_visible(localizador).text


class PaginaConSesion(BasePage):
    """Página interna de la tienda: tiene barra superior con carrito y menú lateral."""

    TITULO = data_test("title")
    LOGO = (By.CLASS_NAME, "app_logo")
    ICONO_CARRITO = data_test("shopping-cart-link")
    BADGE_CARRITO = data_test("shopping-cart-badge")
    BOTON_MENU = (By.ID, "react-burger-menu-btn")
    LINK_LOGOUT = data_test("logout-sidebar-link")
    LINK_RESET = data_test("reset-sidebar-link")

    def titulo(self):
        """Devuelve el encabezado de la sección, por ejemplo 'Products' o 'Your Cart'."""
        return self.texto(self.TITULO)

    def logo(self):
        return self.texto(self.LOGO)

    # --- Carrito ---

    def cantidad_en_carrito(self):
        """Cantidad que muestra el badge del carrito.

        SauceDemo elimina el badge del DOM cuando el carrito está vacío, por eso se
        devuelve 0 en lugar de lanzar una excepción.
        """
        badges = self.driver.find_elements(*self.BADGE_CARRITO)
        return int(badges[0].text) if badges else 0

    def hay_badge_carrito(self):
        return self.existe(self.BADGE_CARRITO)

    def esperar_cantidad_en_carrito(self, esperada):
        """Espera a que el badge muestre `esperada` y devuelve el valor final."""
        self.esperar_que(lambda _: self.cantidad_en_carrito() == esperada)
        return self.cantidad_en_carrito()

    def ir_al_carrito(self):
        from pages.carrito_page import CarritoPage  # Import local: evita ciclos.

        self.log.info("Abriendo el carrito desde la barra superior")
        self.click(self.ICONO_CARRITO)
        return CarritoPage(self.driver).esperar_carga()

    # --- Menú lateral ---

    def cerrar_sesion(self):
        from pages.login_page import LoginPage

        self.log.info("Cerrando sesión desde el menú lateral")
        self.click(self.BOTON_MENU)
        self.click(self.LINK_LOGOUT)
        return LoginPage(self.driver).esperar_carga()

    def resetear_estado_app(self):
        """Usa "Reset App State" del menú lateral y espera que el carrito se vacíe."""
        self.log.info("Reseteando el estado de la aplicación")
        self.click(self.BOTON_MENU)
        self.click(self.LINK_RESET)
        self.esperar_invisible(self.BADGE_CARRITO)
        return self
