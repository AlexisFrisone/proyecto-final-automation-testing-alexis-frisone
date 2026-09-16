"""
helpers.py
==========
Funciones auxiliares, localizadores y datos de prueba compartidos por toda la suite.

Los casos de prueba importan desde este módulo para no repetir lógica ni selectores.
Si SauceDemo cambia un localizador, se corrige acá en un solo lugar y toda la suite
sigue funcionando.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------

URL_BASE = "https://www.saucedemo.com/"
URL_INVENTARIO = "https://www.saucedemo.com/inventory.html"
URL_CARRITO = "https://www.saucedemo.com/cart.html"
URL_CHECKOUT_PASO_1 = "https://www.saucedemo.com/checkout-step-one.html"
URL_CHECKOUT_PASO_2 = "https://www.saucedemo.com/checkout-step-two.html"
URL_CHECKOUT_COMPLETO = "https://www.saucedemo.com/checkout-complete.html"

# Segundos que las esperas explícitas aguardan antes de dar el elemento por ausente.
TIMEOUT_POR_DEFECTO = 10

# Si se pone en True, Chrome corre sin interfaz gráfica (útil para CI).
MODO_HEADLESS = False


# ---------------------------------------------------------------------------
# Datos de prueba
# ---------------------------------------------------------------------------

USUARIO_VALIDO = "standard_user"
USUARIO_BLOQUEADO = "locked_out_user"
USUARIO_INEXISTENTE = "usuario_que_no_existe"
PASSWORD_VALIDA = "secret_sauce"
PASSWORD_INVALIDA = "password_incorrecta"

# Datos usados en el formulario de checkout del flujo end-to-end.
DATOS_CHECKOUT = {
    "nombre": "Alexis",
    "apellido": "Frisone",
    "codigo_postal": "1704",
}

# Mensajes de error que devuelve la aplicación ante cada escenario inválido.
ERROR_CREDENCIALES_INVALIDAS = (
    "Epic sadface: Username and password do not match any user in this service"
)
ERROR_USUARIO_BLOQUEADO = "Epic sadface: Sorry, this user has been locked out."
ERROR_USUARIO_REQUERIDO = "Epic sadface: Username is required"
ERROR_PASSWORD_REQUERIDA = "Epic sadface: Password is required"


# ---------------------------------------------------------------------------
# Localizadores
# ---------------------------------------------------------------------------

class Localizadores:
    """Selectores de la aplicación, agrupados por pantalla.

    Se priorizan los atributos `data-test`, que SauceDemo expone específicamente
    para automatización y no dependen del diseño visual del sitio.
    """

    # --- Pantalla de login ---
    CAMPO_USUARIO = (By.ID, "user-name")
    CAMPO_PASSWORD = (By.ID, "password")
    BOTON_LOGIN = (By.ID, "login-button")
    MENSAJE_ERROR = (By.CSS_SELECTOR, '[data-test="error"]')

    # --- Pantalla de inventario (catálogo) ---
    TITULO_PAGINA = (By.CLASS_NAME, "title")
    LOGO_APP = (By.CLASS_NAME, "app_logo")
    PRODUCTO = (By.CLASS_NAME, "inventory_item")
    NOMBRE_PRODUCTO = (By.CLASS_NAME, "inventory_item_name")
    PRECIO_PRODUCTO = (By.CLASS_NAME, "inventory_item_price")
    BOTON_AGREGAR = (By.CLASS_NAME, "btn_inventory")
    FILTRO_ORDENAMIENTO = (By.CSS_SELECTOR, '[data-test="product_sort_container"]')
    BOTON_MENU = (By.ID, "react-burger-menu-btn")
    LINK_LOGOUT = (By.ID, "logout_sidebar_link")

    # --- Carrito ---
    ICONO_CARRITO = (By.CLASS_NAME, "shopping_cart_link")
    BADGE_CARRITO = (By.CLASS_NAME, "shopping_cart_badge")
    ITEM_CARRITO = (By.CLASS_NAME, "cart_item")
    NOMBRE_ITEM_CARRITO = (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
    BOTON_CHECKOUT = (By.ID, "checkout")
    BOTON_SEGUIR_COMPRANDO = (By.ID, "continue-shopping")

    # --- Checkout ---
    CAMPO_NOMBRE = (By.ID, "first-name")
    CAMPO_APELLIDO = (By.ID, "last-name")
    CAMPO_CODIGO_POSTAL = (By.ID, "postal-code")
    BOTON_CONTINUAR = (By.ID, "continue")
    BOTON_FINALIZAR = (By.ID, "finish")
    TOTAL_COMPRA = (By.CSS_SELECTOR, '[data-test="total-label"]')
    MENSAJE_COMPRA_EXITOSA = (By.CLASS_NAME, "complete-header")
    BOTON_VOLVER_PRODUCTOS = (By.ID, "back-to-products")


# ---------------------------------------------------------------------------
# Manejo del navegador
# ---------------------------------------------------------------------------

def iniciar_driver():
    """Crea y devuelve una instancia de Chrome lista para usar.

    A partir de Selenium 4.6, Selenium Manager descarga y configura ChromeDriver
    automáticamente, por lo que no hace falta instalarlo a mano.
    """
    opciones = Options()
    opciones.add_argument("--start-maximized")
    # Silencia los mensajes de consola de ChromeDriver, que ensucian la salida de pytest.
    opciones.add_experimental_option("excludeSwitches", ["enable-logging"])

    if MODO_HEADLESS:
        opciones.add_argument("--headless=new")
        opciones.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=opciones)
    return driver


# ---------------------------------------------------------------------------
# Esperas explícitas
# ---------------------------------------------------------------------------

def esperar_elemento(driver, localizador, timeout=TIMEOUT_POR_DEFECTO):
    """Espera hasta que el elemento sea visible y lo devuelve.

    Se usa una espera explícita en lugar de `time.sleep()` para que el test avance
    apenas el elemento aparece, sin depender de la velocidad de la máquina o la red.
    """
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(localizador)
    )


def esperar_elemento_clickeable(driver, localizador, timeout=TIMEOUT_POR_DEFECTO):
    """Espera hasta que el elemento esté visible y habilitado para recibir clics."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(localizador)
    )


def esperar_elementos(driver, localizador, timeout=TIMEOUT_POR_DEFECTO):
    """Espera a que exista al menos un elemento con ese localizador y devuelve la lista."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(localizador)
    )
    return driver.find_elements(*localizador)


def esperar_url_contiene(driver, fragmento, timeout=TIMEOUT_POR_DEFECTO):
    """Espera a que la URL actual contenga el fragmento indicado.

    Devuelve True si la redirección ocurrió dentro del timeout.
    """
    return WebDriverWait(driver, timeout).until(EC.url_contains(fragmento))


def elemento_existe(driver, localizador):
    """Indica si el elemento está presente en el DOM, sin lanzar excepción si no lo está.

    Útil para validar ausencias, por ejemplo que el badge del carrito desapareció.
    """
    return len(driver.find_elements(*localizador)) > 0


# ---------------------------------------------------------------------------
# Acciones sobre la aplicación
# ---------------------------------------------------------------------------

def ir_a_login(driver):
    """Navega a la página de login y espera a que el formulario esté disponible."""
    driver.get(URL_BASE)
    esperar_elemento(driver, Localizadores.CAMPO_USUARIO)


def hacer_login(driver, usuario, password):
    """Completa el formulario de login y envía las credenciales.

    No valida el resultado: eso es responsabilidad de cada caso de prueba, lo que
    permite reutilizar la función tanto en escenarios positivos como negativos.
    """
    campo_usuario = esperar_elemento(driver, Localizadores.CAMPO_USUARIO)
    campo_usuario.clear()
    campo_usuario.send_keys(usuario)

    campo_password = esperar_elemento(driver, Localizadores.CAMPO_PASSWORD)
    campo_password.clear()
    campo_password.send_keys(password)

    esperar_elemento_clickeable(driver, Localizadores.BOTON_LOGIN).click()


def login_exitoso(driver, usuario=USUARIO_VALIDO, password=PASSWORD_VALIDA):
    """Inicia sesión y espera la redirección al inventario.

    Es el punto de partida de los tests que necesitan una sesión activa.
    """
    ir_a_login(driver)
    hacer_login(driver, usuario, password)
    esperar_url_contiene(driver, "/inventory.html")


def obtener_mensaje_error(driver):
    """Devuelve el texto del cartel de error que muestra la pantalla de login."""
    return esperar_elemento(driver, Localizadores.MENSAJE_ERROR).text


def obtener_titulo_seccion(driver):
    """Devuelve el encabezado de la sección actual, por ejemplo 'Products'."""
    return esperar_elemento(driver, Localizadores.TITULO_PAGINA).text


def obtener_productos(driver):
    """Devuelve la lista de tarjetas de producto visibles en el catálogo."""
    return esperar_elementos(driver, Localizadores.PRODUCTO)


def obtener_datos_producto(elemento_producto):
    """Extrae nombre y precio de una tarjeta de producto.

    Devuelve un diccionario con las claves 'nombre' y 'precio'.
    """
    return {
        "nombre": elemento_producto.find_element(
            *Localizadores.NOMBRE_PRODUCTO
        ).text,
        "precio": elemento_producto.find_element(
            *Localizadores.PRECIO_PRODUCTO
        ).text,
    }


def agregar_producto_por_indice(driver, indice=0):
    """Agrega al carrito el producto que ocupa la posición indicada.

    Devuelve los datos del producto agregado para poder validarlos más adelante,
    sin necesidad de hardcodear nombres ni precios en los tests.
    """
    productos = obtener_productos(driver)
    producto = productos[indice]
    datos = obtener_datos_producto(producto)
    producto.find_element(*Localizadores.BOTON_AGREGAR).click()
    return datos


def remover_producto_por_indice(driver, indice=0):
    """Quita del carrito el producto indicado desde la página de inventario.

    Tras agregar un producto, el mismo botón cambia su texto a 'Remove', por lo que
    se reutiliza el localizador.
    """
    productos = obtener_productos(driver)
    productos[indice].find_element(*Localizadores.BOTON_AGREGAR).click()


def obtener_contador_carrito(driver):
    """Devuelve la cantidad de ítems que muestra el badge del carrito.

    SauceDemo elimina el badge del DOM cuando el carrito está vacío, por eso se
    devuelve 0 en lugar de lanzar una excepción.
    """
    badges = driver.find_elements(*Localizadores.BADGE_CARRITO)
    if not badges:
        return 0
    return int(badges[0].text)


def ir_al_carrito(driver):
    """Abre el carrito de compras y espera la redirección."""
    esperar_elemento_clickeable(driver, Localizadores.ICONO_CARRITO).click()
    esperar_url_contiene(driver, "/cart.html")


def obtener_nombres_en_carrito(driver):
    """Devuelve la lista de nombres de los productos presentes en el carrito."""
    elementos = driver.find_elements(*Localizadores.NOMBRE_ITEM_CARRITO)
    return [elemento.text for elemento in elementos]


def completar_datos_checkout(driver, nombre, apellido, codigo_postal):
    """Llena el formulario del primer paso del checkout y continúa al resumen."""
    esperar_elemento(driver, Localizadores.CAMPO_NOMBRE).send_keys(nombre)
    esperar_elemento(driver, Localizadores.CAMPO_APELLIDO).send_keys(apellido)
    esperar_elemento(driver, Localizadores.CAMPO_CODIGO_POSTAL).send_keys(codigo_postal)
    esperar_elemento_clickeable(driver, Localizadores.BOTON_CONTINUAR).click()
