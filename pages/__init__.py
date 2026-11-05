"""
Page Objects de SauceDemo.

Cada clase representa una pantalla de la aplicación: conoce sus localizadores y
expone métodos con las acciones que un usuario puede hacer en ella. Los tests sólo
usan estos métodos y nunca interactúan con Selenium directamente.
"""

from pages.carrito_page import CarritoPage
from pages.checkout_page import (
    CheckoutCompletoPage,
    CheckoutInformacionPage,
    CheckoutResumenPage,
)
from pages.detalle_producto_page import DetalleProductoPage
from pages.inventario_page import InventarioPage
from pages.login_page import LoginPage

__all__ = [
    "CarritoPage",
    "CheckoutCompletoPage",
    "CheckoutInformacionPage",
    "CheckoutResumenPage",
    "DetalleProductoPage",
    "InventarioPage",
    "LoginPage",
]
