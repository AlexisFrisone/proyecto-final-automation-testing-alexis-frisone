"""Page Object de la pantalla de login (https://www.saucedemo.com/)."""

from pages.base_page import BasePage, data_test


class LoginPage(BasePage):
    RUTA = ""

    CAMPO_USUARIO = data_test("username")
    CAMPO_PASSWORD = data_test("password")
    BOTON_LOGIN = data_test("login-button")
    MENSAJE_ERROR = data_test("error")
    BOTON_CERRAR_ERROR = data_test("error-button")

    def esperar_carga(self):
        """Espera a que el formulario esté disponible."""
        self.esperar_visible(self.CAMPO_USUARIO)
        return self

    def abrir(self):
        super().abrir()
        return self.esperar_carga()

    def iniciar_sesion(self, usuario, password):
        """Completa el formulario y lo envía, sin validar el resultado.

        Sirve tanto para escenarios positivos como negativos: cada test decide qué
        verificar después.
        """
        self.log.info("Iniciando sesión con el usuario %r", usuario)
        self.escribir(self.CAMPO_USUARIO, usuario)
        self.escribir(self.CAMPO_PASSWORD, password)
        self.click(self.BOTON_LOGIN)
        return self

    def iniciar_sesion_exitosa(self, usuario, password):
        """Inicia sesión y devuelve el inventario, esperando a que termine de cargar."""
        from pages.inventario_page import InventarioPage  # Import local: evita ciclos.

        self.iniciar_sesion(usuario, password)
        return InventarioPage(self.driver).esperar_carga()

    # --- Mensajes de error ---

    def mensaje_error(self):
        return self.texto(self.MENSAJE_ERROR)

    def hay_error(self):
        return self.existe(self.MENSAJE_ERROR)

    def cerrar_error(self):
        self.log.info("Cerrando el cartel de error")
        self.click(self.BOTON_CERRAR_ERROR)
        return self

    def formulario_visible(self):
        return self.existe(self.BOTON_LOGIN)
