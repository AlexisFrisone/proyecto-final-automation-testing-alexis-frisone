"""
Pruebas de API con peticiones encadenadas: cada paso usa datos de la respuesta anterior.

Simulan cómo un cliente real navega la API (usuario → sus posts → comentarios de un
post) y detectan inconsistencias entre recursos relacionados.
"""

import pytest

from utils.validadores import (
    ESQUEMA_COMENTARIO,
    ESQUEMA_POST,
    ESQUEMA_USUARIO,
    errores_de_estructura,
)

pytestmark = [pytest.mark.api, pytest.mark.encadenado]


@pytest.mark.smoke
def test_usuario_sus_posts_y_los_comentarios_de_un_post(api):
    """GET usuario → GET posts de ese usuario → GET comentarios del primer post."""
    # --- Paso 1: obtener un usuario ---
    respuesta_usuario = api.get("/users/2")
    assert respuesta_usuario.status_code == 200
    usuario = respuesta_usuario.json()
    assert not errores_de_estructura(usuario, ESQUEMA_USUARIO), "Estructura de usuario inválida"
    assert "@" in usuario["email"], f"Email inválido: {usuario['email']}"

    # --- Paso 2: sus posts, usando el id obtenido ---
    respuesta_posts = api.get("/posts", params={"userId": usuario["id"]})
    assert respuesta_posts.status_code == 200
    posts = respuesta_posts.json()
    assert posts, f"El usuario {usuario['id']} no tiene posts"
    assert all(post["userId"] == usuario["id"] for post in posts), (
        "Se devolvieron posts que no pertenecen al usuario"
    )

    # --- Paso 3: comentarios del primer post ---
    primer_post = posts[0]
    respuesta_comentarios = api.get(f"/posts/{primer_post['id']}/comments")
    assert respuesta_comentarios.status_code == 200
    comentarios = respuesta_comentarios.json()
    assert comentarios, f"El post {primer_post['id']} no tiene comentarios"
    for comentario in comentarios:
        assert not errores_de_estructura(comentario, ESQUEMA_COMENTARIO)
        assert comentario["postId"] == primer_post["id"], (
            "Hay comentarios asociados a otro post"
        )


def test_crear_un_post_a_nombre_de_un_usuario_existente(api):
    """GET usuario → POST de un post con su id → el post creado queda a su nombre."""
    usuario = api.get("/users/5").json()

    nuevo = {
        "title": f"Post de {usuario['username']}",
        "body": f"Escrito por {usuario['name']}",
        "userId": usuario["id"],
    }
    respuesta = api.post("/posts", nuevo)

    assert respuesta.status_code == 201
    creado = respuesta.json()
    assert creado["userId"] == usuario["id"], "El post no quedó asociado al usuario"
    assert creado["title"] == nuevo["title"]


def test_obtener_modificar_y_borrar_un_post(api):
    """GET post → PUT con el título modificado → DELETE del mismo post."""
    # --- Paso 1: leer el post actual ---
    original = api.get("/posts/7").json()
    assert not errores_de_estructura(original, ESQUEMA_POST)

    # --- Paso 2: reemplazarlo partiendo de los datos leídos ---
    modificado = {**original, "title": original["title"].upper()}
    respuesta_put = api.put(f"/posts/{original['id']}", modificado)
    assert respuesta_put.status_code == 200
    assert respuesta_put.json()["title"] == modificado["title"], "El título no se actualizó"
    assert respuesta_put.json()["body"] == original["body"], "El PUT alteró el cuerpo"

    # --- Paso 3: borrarlo ---
    respuesta_delete = api.delete(f"/posts/{original['id']}")
    assert respuesta_delete.status_code == 200


@pytest.mark.negativo
def test_usuario_inexistente_no_tiene_posts(api):
    """GET de un usuario que no existe → 404, y filtrar posts por ese id da lista vacía."""
    id_inexistente = 11
    assert api.get(f"/users/{id_inexistente}").status_code == 404

    respuesta = api.get("/posts", params={"userId": id_inexistente})
    assert respuesta.status_code == 200
    assert respuesta.json() == [], "Un usuario inexistente no debería tener posts"
