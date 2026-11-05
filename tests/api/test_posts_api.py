"""
Pruebas de API: recurso /posts de JSONPlaceholder (https://jsonplaceholder.typicode.com).

Cubre los métodos GET, POST, PUT y DELETE, validando código de estado, cabeceras,
estructura y contenido del JSON, tanto en escenarios de éxito como de error.

Nota: JSONPlaceholder es una API de práctica que *simula* las escrituras: responde
como si hubiera creado, modificado o borrado el recurso, pero no persiste cambios.
Los datos de prueba se leen de data/api_posts.json.
"""

import pytest

from utils.data_loader import como_parametros, leer_json
from utils.validadores import ESQUEMA_POST, errores_de_estructura, es_respuesta_json

pytestmark = pytest.mark.api

DATOS = leer_json("api_posts.json")


# ---------------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_get_lista_todos_los_posts_con_estructura_valida(api):
    """GET /posts devuelve 200 y la lista completa de posts con la estructura esperada."""
    respuesta = api.get("/posts")

    assert respuesta.status_code == 200, f"Código inesperado: {respuesta.status_code}"
    assert es_respuesta_json(respuesta), "La respuesta no declara contenido JSON"

    posts = respuesta.json()
    assert isinstance(posts, list), "Se esperaba una lista de posts"
    assert len(posts) == DATOS["total_posts"], f"Se esperaban {DATOS['total_posts']} posts"

    for post in posts:
        errores = errores_de_estructura(post, ESQUEMA_POST)
        assert not errores, f"Post {post.get('id')} con estructura inválida: {errores}"

    ids = [post["id"] for post in posts]
    assert len(set(ids)) == len(ids), "Hay posts con id repetido"


@pytest.mark.parametrize("esperado", como_parametros(DATOS["posts_existentes"]))
def test_get_post_por_id_devuelve_el_post_pedido(api, esperado):
    """GET /posts/{id} devuelve 200 y el post con ese id y su autor."""
    respuesta = api.get(f"/posts/{esperado['id']}")

    assert respuesta.status_code == 200
    post = respuesta.json()
    assert not errores_de_estructura(post, ESQUEMA_POST), "Estructura de post inválida"
    assert post["id"] == esperado["id"], f"Se pidió el post {esperado['id']}, llegó {post['id']}"
    assert post["userId"] == esperado["userId"], "El autor del post no es el esperado"
    assert post["title"].strip(), "El post no tiene título"


def test_get_posts_filtrados_por_usuario(api):
    """GET /posts?userId=N devuelve sólo los posts de ese usuario."""
    respuesta = api.get("/posts", params={"userId": 3})

    assert respuesta.status_code == 200
    posts = respuesta.json()
    assert posts, "El filtro por usuario no devolvió posts"
    assert {post["userId"] for post in posts} == {3}, "El filtro devolvió posts de otros usuarios"


@pytest.mark.negativo
@pytest.mark.parametrize("caso", como_parametros(DATOS["ids_inexistentes"]))
def test_get_post_inexistente_devuelve_404(api, caso):
    """GET /posts/{id} con un id que no existe devuelve 404 y un objeto vacío."""
    respuesta = api.get(f"/posts/{caso['id']}")

    assert respuesta.status_code == 404, (
        f"Se esperaba 404 para el id {caso['id']!r}, se obtuvo {respuesta.status_code}"
    )
    assert respuesta.json() == {}, "El cuerpo de un 404 debería ser un objeto vacío"


@pytest.mark.negativo
def test_get_filtro_por_usuario_inexistente_devuelve_lista_vacia(api):
    """Filtrar por un usuario que no existe no es un error: responde 200 con lista vacía."""
    respuesta = api.get("/posts", params={"userId": 9999})

    assert respuesta.status_code == 200
    assert respuesta.json() == [], "Se esperaba una lista vacía"


@pytest.mark.negativo
def test_get_recurso_inexistente_devuelve_404(api):
    """Un endpoint que no existe en la API responde 404."""
    assert api.get("/recurso-que-no-existe").status_code == 404


# ---------------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.parametrize("caso", como_parametros(DATOS["posts_nuevos"]))
def test_post_crea_un_post_y_devuelve_sus_datos(api, caso):
    """POST /posts devuelve 201, los datos enviados y un id nuevo asignado por la API."""
    cuerpo = caso["cuerpo"]
    respuesta = api.post("/posts", cuerpo)

    assert respuesta.status_code == 201, f"Código inesperado: {respuesta.status_code}"
    creado = respuesta.json()
    assert not errores_de_estructura(creado, ESQUEMA_POST), "Estructura del post creado inválida"
    for campo, valor in cuerpo.items():
        assert creado[campo] == valor, f"'{campo}' llegó como {creado[campo]!r}, se envió {valor!r}"
    assert creado["id"] > DATOS["total_posts"], "El id asignado debería ser uno nuevo"


# ---------------------------------------------------------------------------
# PUT
# ---------------------------------------------------------------------------

def test_put_reemplaza_un_post_existente(api):
    """PUT /posts/{id} devuelve 200 y el post con el contenido reemplazado."""
    nuevo = DATOS["post_actualizado"]
    respuesta = api.put(f"/posts/{nuevo['id']}", nuevo)

    assert respuesta.status_code == 200
    assert respuesta.json() == nuevo, f"El post actualizado no coincide: {respuesta.json()}"


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_delete_elimina_un_post(api):
    """DELETE /posts/{id} devuelve 200 y un cuerpo vacío."""
    respuesta = api.delete("/posts/1")

    assert respuesta.status_code == 200, f"Código inesperado: {respuesta.status_code}"
    assert respuesta.json() == {}, "El DELETE debería responder un objeto vacío"
