# Framework de automatización de pruebas — SauceDemo (UI) + JSONPlaceholder (API)

Trabajo final integrador del curso de QA Automation. Es un framework de pruebas automatizadas
en Python que combina:

- **Pruebas de UI** con Selenium WebDriver sobre [SauceDemo](https://www.saucedemo.com/), una
  tienda online de práctica, usando el patrón **Page Object Model**.
- **Pruebas de API** con la biblioteca Requests sobre
  [JSONPlaceholder](https://jsonplaceholder.typicode.com/), una API REST pública de práctica.
- **Datos de prueba externos** (CSV y JSON) para parametrizar los casos.
- **Reporte HTML** con estado, duración y captura de pantalla de cada test de UI fallido.
- **Logging** de los pasos clave de cada test.
- **Integración continua** con GitHub Actions.

---

## Propósito del proyecto

Construir una base de automatización mantenible y fácil de extender, que:

1. Verifique los flujos principales de una tienda online: login, navegación del catálogo,
   carrito y checkout completo, incluyendo escenarios negativos (credenciales inválidas, usuario
   bloqueado, formularios incompletos, acceso sin sesión).
2. Valide una API REST: códigos de estado, estructura y contenido de las respuestas JSON con
   GET, POST, PUT y DELETE, en casos de éxito y de error, y flujos donde una petición depende
   del resultado de otra.
3. Deje evidencia clara de cada ejecución (reporte HTML, capturas y log) para depurar rápido.

---

## Tecnologías utilizadas

| Tecnología | Versión | Rol en el proyecto |
|---|---|---|
| **Python** | 3.12 | Lenguaje principal |
| **Pytest** | 9.x | Framework de testing, fixtures y parametrización |
| **Selenium WebDriver** | 4.x | Automatización del navegador (pruebas de UI) |
| **Requests** | 2.x | Cliente HTTP (pruebas de API) |
| **pytest-html** | 4.x | Reporte HTML de resultados |
| **Google Chrome** | Última estable | Navegador de las pruebas de UI |
| **Git / GitHub** | — | Control de versiones |
| **GitHub Actions** | — | Ejecución automática de la suite en cada push |

> **Sobre el driver:** desde Selenium 4.6 se incluye *Selenium Manager*, que descarga y configura
> ChromeDriver automáticamente. No hace falta instalarlo a mano ni usar `webdriver-manager`.

---

## Estructura del proyecto

```
entregaFinal/
├── pages/                         # Page Objects (una clase por pantalla de SauceDemo)
│   ├── base_page.py               # BasePage (esperas y acciones) y PaginaConSesion (header y menú)
│   ├── login_page.py
│   ├── inventario_page.py
│   ├── detalle_producto_page.py
│   ├── carrito_page.py
│   └── checkout_page.py           # Información, resumen y confirmación
├── tests/
│   ├── ui/                        # Pruebas de interfaz (Selenium)
│   │   ├── test_login.py
│   │   ├── test_inventario.py
│   │   ├── test_carrito.py
│   │   ├── test_checkout.py
│   │   └── test_flujos_e2e.py
│   └── api/                       # Pruebas de API (Requests)
│       ├── test_posts_api.py
│       └── test_flujos_encadenados_api.py
├── utils/
│   ├── config.py                  # URLs, timeouts, credenciales demo y modo headless
│   ├── driver_factory.py          # Creación de Chrome
│   ├── api_client.py              # Cliente HTTP con logging de cada petición
│   ├── data_loader.py             # Lectura de CSV/JSON y armado de parámetros
│   ├── validadores.py             # Esquemas y validación de estructura JSON
│   └── logger.py                  # Loggers del framework
├── data/                          # Datos de prueba externos
│   ├── login_usuarios.csv
│   ├── productos.json
│   ├── checkout.json
│   └── api_posts.json
├── .github/workflows/pruebas.yml  # Pipeline de GitHub Actions
├── conftest.py                    # Fixtures, capturas de pantalla y personalización del reporte
├── pytest.ini                     # Configuración de pytest, reporte, logging y marcadores
├── requirements.txt
└── reports/                       # Generado en cada ejecución (ignorado por Git)
```

### Cómo está organizado

- **Page Object Model.** Cada pantalla tiene su clase en `pages/` con sus localizadores y métodos
  que representan acciones del usuario (`iniciar_sesion`, `agregar_por_nombre`, `ir_al_checkout`,
  `finalizar`...). Los tests **nunca** usan Selenium directamente: sólo llaman a esos métodos y
  hacen las aserciones. Si SauceDemo cambia un selector, se corrige en un único lugar.
- **Navegación fluida.** Los métodos que cambian de pantalla devuelven el Page Object de la
  pantalla siguiente, ya cargada. Por ejemplo:
  `inventario.ir_al_carrito().ir_al_checkout().continuar_con_datos(...).finalizar()`.
- **Esperas explícitas.** Todas las esperas usan `WebDriverWait` + `expected_conditions`; no hay
  ningún `time.sleep()`.
- **Localizadores estables.** Se priorizan los atributos `data-test` que expone SauceDemo.
- **Tests independientes.** Cada test de UI abre un Chrome nuevo y lo cierra al terminar, así la
  falla de uno no afecta a los demás y se pueden correr en cualquier orden.

---

## Instalación de dependencias

Requisitos: **Python 3.10 o superior**, **Google Chrome** y **Git**.

```bash
# 1. Clonar el repositorio
git clone https://github.com/USUARIO/NOMBRE-DEL-REPO.git
cd NOMBRE-DEL-REPO

# 2. Crear y activar un entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows (PowerShell)
# source .venv/bin/activate         # Linux / macOS

# 3. Instalar las dependencias
pip install -r requirements.txt
```

> Si PowerShell bloquea la activación del entorno, ejecutar una sola vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

---

## Cómo ejecutar las pruebas

`pytest.ini` ya incluye las opciones del reporte, así que basta con:

```bash
pytest                      # Suite completa (UI + API), con Chrome visible
pytest --headless           # Suite completa sin abrir ventanas de Chrome
```

También se puede activar el modo headless con la variable de entorno `HEADLESS=true`, que es lo
que usa GitHub Actions.

### Ejecutar una parte de la suite

```bash
pytest tests/api                    # Sólo API (no abre el navegador, tarda segundos)
pytest tests/ui                     # Sólo UI
pytest tests/ui/test_login.py       # Un archivo
pytest "tests/ui/test_login.py::test_logout_cierra_la_sesion"   # Un test puntual

pytest -m smoke                     # Por marcador
pytest -m "ui and negativo"         # Combinando marcadores
pytest -k carrito                   # Por nombre
```

Marcadores disponibles (definidos en `pytest.ini`): `ui`, `api`, `smoke`, `login`, `inventario`,
`carrito`, `checkout`, `negativo`, `e2e`, `encadenado`.

### Opciones útiles

```bash
pytest -x                 # Detenerse en el primer fallo
pytest --lf               # Volver a correr sólo los que fallaron la última vez
pytest -o log_cli=true    # Ver el log en vivo en la consola
```

---

## Datos de prueba y parametrización

Los datos viven en `data/` y cada fila u objeto se convierte en una ejecución independiente del
test, con un identificador legible (por ejemplo `test_login_con_credenciales_invalidas_muestra_error[usuario_bloqueado]`).
**Para agregar un escenario alcanza con editar el archivo de datos**, sin tocar el código.

| Archivo | Lo usa | Contenido |
|---|---|---|
| `login_usuarios.csv` | `test_login.py` | Usuarios válidos (`resultado=exito`) e inválidos (`resultado=error`) con el mensaje esperado |
| `productos.json` | `test_carrito.py`, `test_inventario.py` | Combinaciones de productos para el carrito y criterios de ordenamiento |
| `checkout.json` | `test_checkout.py` | Compradores válidos (incluye acentos y textos largos) y formularios incompletos |
| `api_posts.json` | `test_posts_api.py` | Posts existentes, ids inexistentes y cuerpos para POST/PUT |

---

## Casos de prueba

**65 tests en total** (46 de UI y 19 de API, contando cada combinación de datos como un caso).

### UI — SauceDemo

| Archivo | Qué cubre |
|---|---|
| `test_login.py` | Login exitoso con 4 tipos de usuario; 9 escenarios negativos desde CSV (contraseña incorrecta, usuario inexistente o bloqueado, campos vacíos, mayúsculas, espacios); cerrar el cartel de error; acceso directo sin sesión; logout |
| `test_inventario.py` | Catálogo completo con nombre y precio; los 4 ordenamientos; detalle de producto consistente con el catálogo |
| `test_carrito.py` | Agregar 1, 2 y 3 productos; agregar desde el detalle; quitar desde el catálogo y desde el carrito; agregar todo el catálogo; persistencia al recargar y reordenar; "Reset App State" |
| `test_checkout.py` | Compra completa de punta a punta con 3 compradores (valida subtotal, impuesto y total); 4 formularios incompletos; cancelar desde el resumen |
| `test_flujos_e2e.py` | Comprar el producto más barato; seguir comprando antes de pagar; dos compras seguidas; carrito que sobrevive a un logout; usuario bloqueado sin acceso |

### API — JSONPlaceholder

| Archivo | Qué cubre |
|---|---|
| `test_posts_api.py` | `GET` de la lista (estructura de los 100 posts), por id y con filtro; `GET` con 4 ids inexistentes (404); endpoint inexistente; `POST` (201) con 2 cuerpos; `PUT` (200); `DELETE` (200) |
| `test_flujos_encadenados_api.py` | Usuario → sus posts → comentarios; crear un post a nombre de un usuario obtenido antes; leer → modificar → borrar un post; usuario inexistente sin posts |

> JSONPlaceholder **simula** las escrituras: responde como si creara, modificara o borrara, pero
> no guarda los cambios. Por eso los flujos encadenados usan los datos de una respuesta como
> entrada de la siguiente petición, en lugar de volver a leer un recurso recién creado.

---

## Cómo interpretar los reportes

Cada ejecución genera en `reports/`:

| Archivo | Contenido |
|---|---|
| `reporte.html` | Reporte de resultados. Es autocontenido: se abre con cualquier navegador y se puede compartir como un único archivo |
| `ejecucion.log` | Log completo (nivel DEBUG) de toda la ejecución |
| `capturas/` | Capturas PNG de los tests de UI que fallaron (sólo se crea si hubo fallos) |

### El reporte HTML

- **Encabezado:** fecha, duración total, entorno y las URLs contra las que se corrió.
- **Resumen:** cantidad de tests por estado. Haciendo clic en cada estado (*Passed*, *Failed*,
  *Skipped*, *Error*...) se filtra la tabla.
- **Tabla de resultados:** una fila por test con su **resultado**, su **nombre** (incluye entre
  corchetes el caso de datos, por ejemplo `[usuario_bloqueado]`), una **descripción** tomada del
  docstring del test y su **duración**. Las columnas se pueden ordenar con un clic.
- **Detalle de cada fila:** al expandirla se ve el log capturado del test (los pasos que ejecutó y,
  en API, cada petición con su código y tiempo de respuesta). Si el test falló, además se ve:
  - el error y la línea del `assert` que no se cumplió, con el valor esperado y el obtenido;
  - en los tests de UI, la **captura de pantalla** del momento del fallo y la URL en la que
    estaba el navegador.

### Capturas de pantalla

Cuando un test de UI falla, se guarda automáticamente una captura con el nombre del test y la
fecha y hora, por ejemplo:

```
reports/capturas/test_login_con_credenciales_validas_lleva_al_catalogo_usuario_estandar_20261104_213015.png
```

### Log de ejecución

`reports/ejecucion.log` registra, con fecha y hora, el inicio y fin de cada test, cada acción
sobre las páginas (login, productos agregados, datos del checkout...) y cada petición HTTP con su
método, URL, código, tiempo de respuesta y cuerpo. Ejemplo:

```
2026-11-04 21:10:02 [INFO    ] framework.conftest: ===== INICIO: tests/api/test_posts_api.py::test_delete_elimina_un_post =====
2026-11-04 21:10:02 [INFO    ] framework.api: → DELETE https://jsonplaceholder.typicode.com/posts/1
2026-11-04 21:10:02 [INFO    ] framework.api: ← 200 OK (182 ms)
```

---

## Integración continua (GitHub Actions)

El workflow `.github/workflows/pruebas.yml` se ejecuta en cada `push` y `pull request` (y también
a mano desde la pestaña *Actions*). Instala Python y las dependencias, corre toda la suite en
modo headless y publica la carpeta `reports/` (reporte HTML, log y capturas) como **artefacto**
descargable desde el resumen de la ejecución, aun cuando haya tests fallidos.

---

## Cómo agregar nuevas pruebas

1. **Nuevo escenario con datos existentes:** agregar una fila al CSV o un objeto al JSON en `data/`.
2. **Nueva pantalla:** crear su Page Object en `pages/` heredando de `PaginaConSesion` (o de
   `BasePage` si no requiere sesión), con sus localizadores y acciones.
3. **Nuevo test:** ubicarlo en `tests/ui/` o `tests/api/`, usar las fixtures `login_page`,
   `inventario`, `driver` o `api`, y marcarlo con los marcadores que correspondan.

---

## Autor

Alexis Frisone — Curso de QA Automation
