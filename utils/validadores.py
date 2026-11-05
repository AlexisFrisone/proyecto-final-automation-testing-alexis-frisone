"""
validadores.py
==============
Funciones de apoyo para validar la estructura de las respuestas JSON de la API.

Un "esquema" es un diccionario `{campo: tipo}`. Por ejemplo:

    ESQUEMA_POST = {"userId": int, "id": int, "title": str, "body": str}

La validación verifica que estén todos los campos y que cada uno tenga el tipo
esperado, y devuelve la lista de problemas encontrados (vacía si todo está bien),
para que el assert del test pueda mostrar un mensaje claro.
"""

# --- Esquemas de los recursos de JSONPlaceholder ---
ESQUEMA_POST = {"userId": int, "id": int, "title": str, "body": str}
ESQUEMA_USUARIO = {
    "id": int, "name": str, "username": str, "email": str,
    "address": dict, "phone": str, "website": str, "company": dict,
}
ESQUEMA_COMENTARIO = {"postId": int, "id": int, "name": str, "email": str, "body": str}


def errores_de_estructura(objeto, esquema):
    """Compara un objeto JSON contra un esquema y devuelve la lista de diferencias."""
    if not isinstance(objeto, dict):
        return [f"se esperaba un objeto JSON y se recibió {type(objeto).__name__}"]

    errores = []
    for campo, tipo in esquema.items():
        if campo not in objeto:
            errores.append(f"falta el campo '{campo}'")
        elif not isinstance(objeto[campo], tipo):
            errores.append(
                f"'{campo}' debería ser {tipo.__name__} y es "
                f"{type(objeto[campo]).__name__} ({objeto[campo]!r})"
            )
    return errores


def es_respuesta_json(respuesta):
    """Indica si la respuesta HTTP declara contenido JSON en su Content-Type."""
    return "application/json" in respuesta.headers.get("Content-Type", "")
