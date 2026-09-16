# Automatización de pruebas E2E — SauceDemo

Pre-entrega del curso de QA Automation. Suite de pruebas automatizadas sobre
[www.saucedemo.com](https://www.saucedemo.com/) desarrollada con Python, Pytest y Selenium WebDriver.

---

## Propósito del proyecto

El objetivo es automatizar los flujos básicos de navegación de una aplicación web de e-commerce,
aplicando estrategias de localización de elementos, esperas explícitas y validación de estados.

El sitio elegido, SauceDemo, es una aplicación demo diseñada específicamente para prácticas de
testing, lo que permite trabajar sobre un entorno estable y reproducible.

La suite cubre tres flujos de negocio:

1. **Login** — autenticación con credenciales válidas (`standard_user` / `secret_sauce`) y
   validación de la redirección a `/inventory.html`.
2. **Navegación y catálogo** — verificación del título de la página, presencia de productos
   visibles y de los elementos principales de la interfaz (menú lateral, filtro de ordenamiento,
   ícono del carrito).
3. **Interacción con el carrito** — agregado de un producto, verificación del incremento del
   contador del carrito y comprobación de que el ítem aparece correctamente en el detalle.

Todas las validaciones utilizan **esperas explícitas** (`WebDriverWait` + `expected_conditions`)
en lugar de esperas fijas, para que las pruebas sean estables y no dependan de la velocidad de
la conexión o de la máquina donde se ejecuten.

---

## Tecnologías utilizadas

| Tecnología | Versión | Rol en el proyecto |
|---|---|---|
| **Python** | 3.11+ | Lenguaje principal |
| **Selenium WebDriver** | 4.x | Automatización del navegador |
| **Pytest** | 8.x | Framework de testing y ejecución |
| **pytest-html** | 4.x | Generación del reporte de resultados en HTML |
| **Git / GitHub** | — | Control de versiones y entrega del proyecto |
| **Google Chrome** | Última estable | Navegador objetivo de las pruebas |

> **Nota sobre el driver:** a partir de Selenium 4.6 se incluye *Selenium Manager*, que descarga
> y configura ChromeDriver de forma automática. No hace falta instalarlo a mano ni usar
> `webdriver-manager`.

---

## Estructura del proyecto

```
pre-entrega-final/
├── tests/                  # Casos de prueba, organizados por tipo
│   ├── positive/           # Flujos exitosos (happy path)
│   ├── negative/           # Escenarios de error y validaciones fallidas
│   ├── edge/               # Casos borde y condiciones límite
│   └── e2e/                # Flujos completos de punta a punta
├── helpers/                # Funciones auxiliares y localizadores reutilizables
├── reports/                # Reportes HTML generados (ignorado por Git)
├── .gitignore              # Exclusiones de Git (venv, reportes, cachés)
└── README.md               # Este archivo
```

### Criterio de organización

Los casos de prueba están separados en carpetas según su naturaleza, lo que permite ejecutar
subconjuntos de la suite de forma independiente y facilita el mantenimiento a medida que el
proyecto crece:

| Carpeta | Contiene | Ejemplos |
|---|---|---|
| `positive/` | Flujos que deben completarse correctamente | Login con credenciales válidas, agregar producto al carrito |
| `negative/` | Escenarios donde el sistema debe rechazar la acción | Login con contraseña incorrecta, usuario bloqueado |
| `edge/` | Condiciones límite y comportamientos poco frecuentes | Campos vacíos, carrito sin ítems, orden de productos |
| `e2e/` | Recorridos completos que atraviesan varias pantallas | Login → catálogo → carrito |

La lógica compartida (configuración del driver, acción de login, lectura de datos de producto,
localizadores) vive en `helpers/`, de modo que los archivos de test contengan únicamente el caso
de prueba y sus aserciones. Esta separación cumple el requisito de organizar el código en
módulos diferenciados entre tests y funciones auxiliares.

La carpeta `reports/` está incluida en `.gitignore`: los reportes son artefactos generados en
cada ejecución y no forman parte del código versionado.

---

## Requisitos previos

- **Python 3.11 o superior** — verificar con `python --version`
- **Google Chrome** instalado
- **Git** (para clonar el repositorio)

---

## Instalación de dependencias

### 1. Clonar el repositorio

```bash
git clone https://github.com/USUARIO/NOMBRE-DEL-REPO.git
cd NOMBRE-DEL-REPO
```

### 2. Crear y activar un entorno virtual

Aísla las dependencias del proyecto del resto del sistema.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Una vez activado, el prompt muestra el prefijo `(.venv)`.

> Si PowerShell bloquea la activación, ejecutar una sola vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### 3. Verificar la instalación

```bash
pytest --version
```

---

## Cómo ejecutar las pruebas

### Ejecución completa con reporte HTML

Es el comando principal de entrega. Corre toda la suite y deja el reporte en `reports/`:

```bash
pytest tests/ -v --html=reports/reporte.html --self-contained-html
```

| Parámetro | Función |
|---|---|
| `tests/` | Directorio raíz de los casos de prueba |
| `-v` | Modo verbose: muestra el nombre y resultado de cada test |
| `--html=reports/reporte.html` | Genera el reporte de resultados en HTML |
| `--self-contained-html` | Embebe estilos y scripts en un único archivo, para poder compartirlo |

Al finalizar, se abre `reports/reporte.html` con cualquier navegador: detalla cada caso
ejecutado, su duración y el resultado obtenido.

> Pytest crea la carpeta `reports/` automáticamente si no existe.

### Ejecutar un subconjunto de la suite

Gracias a la organización por carpetas, se puede acotar la ejecución:

```bash
# Solo los casos positivos
pytest tests/positive -v

# Solo los negativos
pytest tests/negative -v

# Solo los flujos end-to-end
pytest tests/e2e -v

# Casos positivos y borde, con reporte
pytest tests/positive tests/edge -v --html=reports/reporte-parcial.html
```

### Ejecutar un archivo o un caso puntual

```bash
# Un archivo completo
pytest tests/positive/test_login.py -v

# Un único caso de prueba
pytest tests/positive/test_login.py::test_login_exitoso -v

# Todos los tests cuyo nombre contenga "carrito"
pytest tests/ -v -k "carrito"
```

### Opciones útiles durante el desarrollo

```bash
# Detenerse en el primer fallo
pytest tests/ -v -x

# Salida detallada de las aserciones fallidas
pytest tests/ -v --tb=long

# Volver a correr solamente los tests que fallaron la última vez
pytest tests/ -v --lf
```

---

## Casos de prueba incluidos

| Categoría | Test | Validación |
|---|---|---|
| `positive/` | `test_login_exitoso` | La URL contiene `/inventory.html` y el título `Products` / `Swag Labs` está presente |
| `positive/` | `test_navegacion_catalogo` | Título correcto, al menos un producto visible, menú y filtro de ordenamiento presentes |
| `positive/` | `test_agregar_producto_al_carrito` | El contador del carrito se incrementa a 1 y el producto aparece en el detalle del carrito |
| `negative/` | `test_login_credenciales_invalidas` | Se muestra el mensaje de error y no hay redirección a `/inventory.html` |
| `edge/` | `test_login_campos_vacios` | El sistema exige el campo usuario antes de permitir el envío |
| `e2e/` | `test_flujo_compra_completo` | Recorrido login → catálogo → carrito con validación en cada etapa |

---

## Autor

Alexis Frisone — Curso de QA Automation