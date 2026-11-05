"""
api_client.py
=============
Cliente HTTP para la API pública JSONPlaceholder, construido sobre `requests`.

Encapsula la URL base, el timeout y el registro en el log de cada petición y su
respuesta, de modo que los tests de API sólo expresan *qué* piden y *qué* validan.
"""

import json

import requests

from utils.config import TIMEOUT_API, URL_API
from utils.logger import obtener_logger

log = obtener_logger("api")

# Largo máximo del cuerpo de respuesta que se vuelca al log, para no inundarlo
# cuando un endpoint devuelve listas grandes.
MAX_LARGO_CUERPO_LOG = 500


class ApiClient:
    """Cliente reutilizable para hacer peticiones a una API REST.

    Usa una `requests.Session` para reutilizar la conexión y compartir cabeceras
    entre peticiones.
    """

    def __init__(self, url_base=URL_API, timeout=TIMEOUT_API):
        self.url_base = url_base.rstrip("/")
        self.timeout = timeout
        self.sesion = requests.Session()
        self.sesion.headers.update({
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json",
        })

    # ------------------------------------------------------------------
    # Métodos HTTP
    # ------------------------------------------------------------------

    def get(self, ruta, params=None):
        """Envía un GET a `ruta` (por ejemplo '/posts/1') con query params opcionales."""
        return self._enviar("GET", ruta, params=params)

    def post(self, ruta, cuerpo):
        """Envía un POST con `cuerpo` serializado como JSON."""
        return self._enviar("POST", ruta, json=cuerpo)

    def put(self, ruta, cuerpo):
        """Envía un PUT (reemplazo completo del recurso) con `cuerpo` como JSON."""
        return self._enviar("PUT", ruta, json=cuerpo)

    def delete(self, ruta):
        """Envía un DELETE sobre el recurso indicado."""
        return self._enviar("DELETE", ruta)

    def cerrar(self):
        """Libera las conexiones abiertas por la sesión."""
        self.sesion.close()

    # ------------------------------------------------------------------
    # Implementación interna
    # ------------------------------------------------------------------

    def _enviar(self, metodo, ruta, **kwargs):
        """Envía la petición, registra ida y vuelta en el log y devuelve la respuesta."""
        url = f"{self.url_base}/{ruta.lstrip('/')}"
        log.info("→ %s %s", metodo, url)
        if kwargs.get("params"):
            log.debug("  query params: %s", kwargs["params"])
        if kwargs.get("json") is not None:
            log.debug("  cuerpo enviado: %s", json.dumps(kwargs["json"], ensure_ascii=False))

        respuesta = self.sesion.request(metodo, url, timeout=self.timeout, **kwargs)

        duracion_ms = respuesta.elapsed.total_seconds() * 1000
        log.info("← %s %s (%.0f ms)", respuesta.status_code, respuesta.reason, duracion_ms)
        log.debug("  cuerpo recibido: %s", respuesta.text[:MAX_LARGO_CUERPO_LOG])
        return respuesta
