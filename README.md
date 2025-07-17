# 🏡 HomeCat: Asistente Inmobiliario Inteligente

**HomeCat** es una inteligencia artificial conversacional especializada en el asesoramiento inmobiliario personalizado. Funciona como un asesor humano capaz de entender el lenguaje natural, extraer preferencias del usuario en tiempo real y recomendar propiedades  **reales** , disponibles desde una base de datos actualizada.

Este proyecto forma parte de un portafolio profesional y refleja una arquitectura de software modular, clara y adaptable para entornos productivos o educativos.

---

## ⚡ TL;DR

HomeCat es un asistente de inteligencia artificial conversacional que recomienda inmuebles reales a partir de una conversación natural. Extrae filtros como ciudad, tipo, precio o habitaciones y muestra resultados desde una base de datos. Funciona con un modelo de lenguaje local (Mistral 7B) sin conexión a internet, utilizando FastAPI y un frontend responsivo. Ideal para entornos de producción o portafolio técnico avanzado.

---

## 🚀 ¿Qué hace único a HomeCat?

- 🤖 Usa un modelo de lenguaje **local**, sin depender de servicios externos (offline-ready).
- 🧠 **Extrae filtros e intenciones** reales del usuario usando embeddings, regex y lógica semántica.
- 🔐 **No muestra propiedades sin confirmación real**, asegurando relevancia y privacidad.
- 🏗️ Arquitectura **modular y asincrónica**, diseñada con FastAPI y preparada para producción local.
- 💬 Simula un **asesor humano empático** con prompting estructurado y salida enriquecida.
- 🖼️ Interfaz interactiva con lightbox, animaciones y diseño adaptado para móviles.

---

## 📸 Vista Previa de HomeCat

A continuación se presentan capturas reales del funcionamiento de HomeCat desde la interfaz web:

### 🌀 Pantalla de Carga Inicial

> Se muestra mientras el backend y el modelo LLM se inicializan.

![Preparando HomeCat...](frontend/static/img/loading.png)

### 💬 Indicador de Escritura

> Cuando el usuario envía un mensaje, HomeCat simula que está pensando y escribiendo una respuesta.

![HomeCat está pensando...](frontend/static/img/thinking.png)

### 🏨 Respuesta con Propiedad Real

> HomeCat recomienda una propiedad real en base a los filtros conversacionales del usuario.

![Respuesta](frontend/static/img/respuesta.png)

### ❌ Página de Error 404 (como ejemplo)

> Si se accede a una ruta que desencadene un error (400, 401, 403, 40, 405, 409, 422, 500, 502 o 504), el sistema sirve una página de error personalizada para el respectivo caso con diseño responsivo.

![Página de Error](frontend/static/img/pagina_error.png)

### 📱 Vista en Dispositivo Móvil

> Diseño adaptado y completamente usable en pantallas pequeñas, con scroll automático y layout fluido.

![Vista en móviles](frontend/static/img/movil.png)

---

## 📈 Características Principales

* 🔍 Extracción inteligente de filtros con regex semánticas, fuzzy matching y embeddings (`MiniLM-L6-v2`).
* 🧠 Motor LLM local (`Mistral 7B`, `TinyLLaMA`, etc.) ejecutado mediante `>llama.cpp`.
* 🔐 Sistema de confirmación semántica por regex y similitud coseno para mostrar propiedades solo bajo autorización.
* 🗃️ Recomendación de propiedades reales desde PostgreSQL.
* 💬 Prompting profesional que simula a un asesor humano empático, sin lenguaje artificial ni especulativo.
* 🌐 Frontend interactivo con pantalla de carga animada, indicadores de escritura, errores visuales y lightbox para imágenes.
* 🧹 Arquitectura modular: backend asíncrono (FastAPI), frontend JS modular, memoria por sesión, sistema de flags.
* ⚙️ Control granular de generación (tokens, temperatura, penalizaciones).
* 🔒 Seguridad por token en encabezados (`/get-token`, `/token/onlyjs`).
* ✨ Listo para producción: logs, handlers de error, configuración automática del modelo.

---

## 🪨 Tecnologías y Herramientas Utilizadas

| Tecnología                                 | Uso                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------- |
| **FastAPI**                           | Backend asincrónico para la API REST principal                     |
| **llama.cpp** + `llama-cpp-python` | Motor de inferencia local para el modelo Mistral 7B en formato GGUF |
| **SQLAlchemy**                        | ORM para modelado y acceso a base de datos PostgreSQL               |
| **SentenceTransformers**              | Embeddings semánticos para intención y confirmación              |
| **Pydantic v2**                       | Validación de entrada/salida de datos                              |
| **Uvicorn**                           | Servidor ASGI                                                       |
| **PostgreSQL**                        | Almacenamiento estructurado de inmuebles                            |
| **HTML/CSS/JS (Vanilla)**             | Frontend ligero y responsivo                                        |
| **Bootstrap 5.3**                     | Diseño adaptativo                                                  |
| **Torch**                             | Framework base para embeddings                                      |

---

## 🧠 Arquitectura General

```
ai_inmobiliaria
|-- backend
    |-- api
        |-- utils
            |   auth_utils.py
            |   confirmation_utils.py
            |   dictionaries.py
            |   llm_prompt.py
            |   ubicaciones_guadalajara_de_buga.py
        |   chat.py
        |   filter_extractor.py
        |   main_api.py
        |   routes.py
        |   schemas.py
        |   search_engine.py
    |-- db
        |-- crud
            |   property.py
        |-- models
            |   image.py
            |   property.py
        |-- schemas
            |   property.py
        |   database.py
    |-- llm_engine
        |   llm_engine.py
        |   __init__.py
    |-- memory
        |   memory.py
        |   memory_manager.py
        |   session_store.py
    |-- models
        |   mistral-7b-instruct-v0.2.Q4_K_M.gguf
    |-- prompt
        |   prompt_template.txt
    |   logger_setup.py
|-- frontend
    |-- static
        |-- css
            |   styles.css
            |   styles_errors.css
        |-- img
            |   favicon.ico
            |   logo-homecat.png
        |-- js
            |   App.js
            |   ChatManager.js
            |   LightboxManager.js
            |   main.js
            |   StatusIndicatorManager.js
            |   TypingIndicatorManager.js
            |   UIManager.js
            |   utils.js
        |-- lottie
            |   401.json
            |   404.json
            |   500.json
            |   Error.json
    |-- templates
        |   400.html
        |   401.html
        |   403.html
        |   404.html
        |   405.html
        |   409.html
        |   422.html
        |   500.html
        |   502.html
        |   504.html
        |   index.html
|-- local_tests
    |   main_local.py
    |   test_mistral.py
|-- tests
    |-- assets
        |   test_data.sql
    |-- utils
        |   conftest.py
        |   db_setup.py
    |   test_concurrency.py
    |   __init__.py
|   .env
|   .gitignore
|   Procfile
|   pytest.ini
|   README.md
|   requirements.txt
```

---

## 🔐 Seguridad y control

* Uso de `API_SECRET` y `WEB_API_SECRET`, gestionados desde `.env`.
* Rutas especiales:

  * `GET /get-token`: entrega tokens via headers, protegidos.
  * `GET /token/onlyjs`: asegura que el frontend no inyecta tokens directamente en HTML.

---

## 🧹 Flujo Conversacional

1. El usuario inicia una conversación natural ("Hola", "Quiero una casa en La Ventura...").
2. HomeCat extrae filtros: tipo, ciudad, barrio, habitaciones, área, etc.
3. Si se detecta intención de ver resultados (`es_confirmacion_usuario`), el sistema activa la búsqueda.
4. Se consulta la propiedad ideal usando coincidencia ponderada.
5. La IA redacta la respuesta usando un prompt con estilo humano-profesional.

---

## 🧠 Confirmación inteligente

El sistema no muestra propiedades hasta que detecta confirmación real.
La detección se hace con:

* Regex especializadas para frases como "quiero verla", "muéstrame opciones", "dale pues".
* Embeddings semánticos que comparan el mensaje del usuario con un set precalculado de frases confirmatorias.

---

## 🖼️ Interfaz y UX

* **Pantalla de carga animada** con efecto pulsante mientras se inicializa el backend.
* **Interacción natural y sin recarga**.
* **Indicador de escritura** simulado ("HomeCat está escribiendo...").
* **Mensajes enriquecidos con HTML y Markdown**.
* **Manejo de errores 4xx/5xx con plantillas dedicadas**.
* **Lightbox de imágenes** para visualización de propiedades.

---

## ⚖️ Diagrama de Flujo Conversacional y Funcional

A continuación se describe el flujo de interacción completo del sistema HomeCat desde el acceso inicial hasta la recomendación de propiedades, incluyendo manejo de errores y rutas especiales.

*Este diagrama de flujo cubre todos los caminos esperados en producción para un usuario regular, así como las rutas técnicas que soportan la funcionalidad de HomeCat.*

```
Inicio del Usuario en / o /start
|
|-- Si NO hay token válido:
|     |-- Redirige automáticamente a /start
|     |-- Muestra pantalla de carga animada (JS + CSS)
|     |-- Solicita token via /get-token (JS)
|     |-- Si se recibe:
|          |-- Almacena en sessionStorage
|          |-- Carga / con token (frontend)
|     |-- Si falla:
|          |-- Muestra error en pantalla con detalles
|
|-- Si SÍ hay token válido:
      |-- Se carga el template HTML principal (frontend)
      |-- Se inyectan los tokens por cabecera
      |-- Se activa el chat (SPA, no recarga la página)
      |-- Se inicia conversación con HomeCat

Conversación con HomeCat
|
|-- HomeCat saluda y presenta si es el primer mensaje
|-- Extrae filtros usando NLP, embeddings y regex
|-- Almacena contexto conversacional y filtros en memoria
|-- Si el sistema lo permite:
|     |-- Envía propiedad real según filtros
|     |-- HomeCat la describe con lenguaje empático y profesional
|-- Si no hay autorización del sistema:
|     |-- HomeCat mantiene la conversación sin mostrar propiedades

Enlaces y Rutas Alternas
|
|-- /get-token
|     |-- Devuelve los dos tokens como cabeceras custom (evita HTML)
|-- /token/onlyjs
|     |-- Usado exclusivamente desde frontend para JS
|-- /static/* y /templates/*
|     |-- Servidos con headers MIME corregidos automáticamente

Manejo de Errores
|
|-- Si ocurre un error 400, 401, 403, 404, 405, 409, 422, 500, 502 o 504:
|     |-- Se sirve una plantilla HTML personalizada desde templates/
|-- Excepciones de validación (422):
|     |-- Se muestra plantilla con detalles de errores
|-- Excepciones no controladas:
|     |-- Log a consola y plantilla genérica 500.html

Sesiones
|
|-- Memoria en RAM por session_id
|-- Guarda filtros, historial, flags, estado y actividad
|-- Se resetea automáticamente tras 1h de inactividad

Backend Principal
|
|-- FastAPI + Rutas en /backend/api/routes.py
|-- Inferencia en /backend/llm_engine/llm_engine.py
|-- Extracción de filtros en /backend/logic/filter_extractor.py
|-- Base de datos consultada desde /backend/logic/search_engine.py

Fin del flujo
```

---

## 🚀 Backend

### Arquitectura General

```
|-- backend
    |-- api
        |-- utils
            |   auth_utils.py
            |   confirmation_utils.py
            |   dictionaries.py
            |   llm_prompt.py
            |   ubicaciones_guadalajara_de_buga.py
        |   chat.py
        |   filter_extractor.py
        |   main_api.py
        |   routes.py
        |   schemas.py
        |   search_engine.py
    |-- db
        |-- crud
            |   property.py
        |-- models
            |   image.py
            |   property.py
        |-- schemas
            |   property.py
        |   database.py
    |-- llm_engine
        |   llm_engine.py
        |   __init__.py
    |-- memory
        |   memory.py
        |   memory_manager.py
        |   session_store.py
    |-- models
        |   mistral-7b-instruct-v0.2.Q4_K_M.gguf
    |-- prompt
        |   prompt_template.txt
    |   logger_setup.py
```

### Componentes Principales

#### 🔍 `filter_extractor.py`

* Regex contextuales para ciudad, barrio, tipo, precio, área, habitaciones, baños y parqueaderos.
* Embeddings (MiniLM-L6-v2) para detectar intenciones como "quiero ver la propiedad".

#### 🔬 `llm_engine.py`

* Ejecuta el modelo `mistral-7b-instruct`.
* Usa `prompt_template.txt` como prompt de sistema.
* Controla generación con temperatura, top_k, top_p, penalizaciones.
* Estructura de prompt tipo:
  ```
  <<SYS>>
  [Instrucciones...]
  <</SYS>>
  Usuario: ...
  Asesor:
  ```

#### 📁 `memory_manager.py`

* Estado por sesión:
  * `history` (mensajes)
  * `filters` (preferencias)
  * `flags`: `filtros_completos`, `mostrar_propiedad`
* Thread-safe con `threading.Lock`.
* Límite de historial configurable.

#### 🏢 `search_engine.py`

* Busca propiedades reales desde la base de datos.
* Ponderación inteligente por coincidencia.
* Devuelve propiedad ideal + metadatos (imágenes, slug).

#### 🔐 `chat.py`

* Orquestador principal:
  * Procesa mensaje
  * Extrae filtros
  * Detecta intención
  * Consulta propiedad ideal
  * Renderiza HTML enriquecido
* Filtra alucinaciones del modelo antes de responder.

#### 📊 `db/models/`

* `Inmueble`: modelo principal.
* `ImagenInmueble`: relación uno a muchos.
* `MapaInmueble`: lat/lon para geolocalización futura.

#### 🔄 `database.py`

* Configura `DATABASE_URL` desde `.env`.
* Provee `get_db()` para inyección de dependencias.

#### 🧩 Extras:

* `/debug/info` muestra estado del modelo y sesiones activas.
* `/session/reset` permite depurar sesión desde frontend.
* `session_store.py` permite persistencia futura en disco o BD.

### Comportamiento del Sistema

#### Flujo Conversacional:

1. Usuario escribe o saluda.
2. Se extraen filtros e intenciones.
3. Si hay suficientes datos y confirmación, se busca propiedad.
4. La propiedad se muestra como respuesta natural y enriquecida.
5. Si no hay datos suficientes, se continúa la conversación.

---

# 🌎 Frontend

## Arquitectura General

```
|-- frontend
    |-- static
        |-- css
            |   styles.css
            |   styles_errors.css
        |-- img
            |   favicon.ico
            |   logo-homecat.png
        |-- js
            |   App.js
            |   ChatManager.js
            |   LightboxManager.js
            |   main.js
            |   StatusIndicatorManager.js
            |   TypingIndicatorManager.js
            |   UIManager.js
            |   utils.js
        |-- lottie
            |   401.json
            |   404.json
            |   500.json
            |   Error.json
    |-- templates
        |   400.html
        |   401.html
        |   403.html
        |   404.html
        |   405.html
        |   409.html
        |   422.html
        |   500.html
        |   502.html
        |   504.html
        |   index.html
```

## Tecnologías

* HTML5 + CSS3 + JS Vanilla.
* Bootstrap 5.3.
* LocalStorage para persistencia.

## Características

* Dark mode completo.
* Sidebar informativa.
* Indicador de actividad: "HomeCat está investigando".
* Scroll automático hacia el final.
* Lightbox de imágenes (ampliación y navegación).
* Layout responsivo.
* Input adaptado a teclado en móvil.
* Contador de caracteres con colores.
* Markdown básico: `**negrita**`, saltos.

## Modularidad en JS

* `UIManager`: renderizado de mensajes, scroll, placeholder.
* `ChatManager`: peticiones al backend, manejo de errores.
* `TypingIndicatorManager`: animación de IA escribiendo.
* `LightboxManager`: navegación entre imágenes.
* Manejadores desacoplados y organizados.

## Mejores Prácticas UX

* Estados visuales: error, sin conexión, respuesta lenta.
* Soporte para Enter / Shift + Enter.
* Indicadores visuales para feedback inmediato.

---

## 🧰 Requisitos del Sistema

### ✅ Requisitos Mínimos (Funciona, pero con limitaciones)

| Componente                  | Detalle                                                                                                                                |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **CPU**               | 4 núcleos físicos / 8 hilos (ej: Intel i7-4790S o AMD Ryzen 5 2500U)                                                                 |
| **RAM**               | 16 GB (puede intercambiar mucho con disco si el modelo es pesado)                                                                      |
| **GPU (opcional)**    | No requerida, pero mejora inferencia si soporta OpenCL o CUDA                                                                          |
| **Almacenamiento**    | SSD con al menos 10 GB libres                                                                                                          |
| **Modelo LLM**        | Mistral 7B `.gguf` Q4 o inferior (4–5 GB de VRAM o RAM compartida)                                                                  |
| **Python**            | 3.11 o superior                                                                                                                        |
| **Base de Datos**     | PostgreSQL 12+ o MySQL (si adaptas el conector SQLAlchemy y driver)                                                                    |
| **Sistema Operativo** | Windows 10/11, macOS 12+, o cualquier Linux moderno (Ubuntu, Arch, etc)                                                                |
| **Requisitos de red** | No necesarios para la IA (offline), pero sí para tokens de frontend si usas autenticación o conexión a una base de datos en la nube |

### 💪 Requisitos Recomendados (Experiencia fluida y profesional)

| Componente                     | Detalle                                                                                                                      |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **CPU**                  | 8 núcleos físicos / 16 hilos (ej: Ryzen 7 5800X, Intel i7-12700K)                                                          |
| **RAM**                  | 32 GB (permite múltiples usuarios o sesiones concurrentes sin swap)                                                         |
| **GPU (opcional)**       | AMD o NVIDIA con al menos 6 GB de VRAM y soporte OpenCL o CUDA                                                               |
| **Almacenamiento**       | SSD NVMe con 20+ GB libres (puede almacenar múltiples modelos `.gguf`)                                                    |
| **Modelo LLM**           | Mistral 7B Q4_K_M o TinyLlama para uso ligero; hasta LLaMA 3 8B Q4 si tienes GPU                                             |
| **Python**               | 3.11.8 o superior (recomendado entorno virtual)                                                                              |
| **Base de Datos**        | PostgreSQL 14+ optimizado, en contenedor o en servidor dedicado                                                              |
| **Sistema Operativo**    | Linux (Ubuntu 22.04+), o Windows 11 Pro WSL2 si usas llama.cpp en modo GPU                                                   |
| **Conexión a Internet** | Necesaria si usas actualización dinámica de modelos, tokens web, conexión a base de datos en la nube o despliegue online |

---

# 📦 Dependencias

```txt
annotated-types==0.7.0
anyio==4.9.0
arrow==1.3.0
certifi==2025.7.9
charset-normalizer==3.4.2
click==8.2.1
colorama==0.4.6
diskcache==5.6.3
dotenv==0.9.9
fastapi==0.116.1
filelock==3.18.0
fsspec==2025.5.1
greenlet==3.2.3
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
huggingface-hub==0.33.4
idna==3.10
iniconfig==2.1.0
Jinja2==3.1.6
joblib==1.5.1
llama_cpp_python==0.3.12
logger-config==0.3
MarkupSafe==3.0.2
mpmath==1.3.0
networkx==3.5
numpy==2.3.1
packaging==25.0
pillow==11.3.0
pluggy==1.6.0
psutil==7.0.0
psycopg2-binary==2.9.10
pydantic==2.11.7
pydantic_core==2.33.2
Pygments==2.19.2
pytest==8.4.1
pytest-asyncio==1.0.0
python-dateutil==2.9.0.post0
python-dotenv==1.1.1
PyYAML==6.0.2
RapidFuzz==3.13.0
regex==2024.11.6
requests==2.32.4
safetensors==0.5.3
scikit-learn==1.7.0
scipy==1.16.0
sentence-transformers==5.0.0
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.41
starlette==0.47.1
sympy==1.14.0
threadpoolctl==3.6.0
tokenizers==0.21.2
torch==2.7.1
tqdm==4.67.1
transformers==4.53.2
types-python-dateutil==2.9.0.20250708
typing-inspection==0.4.1
typing_extensions==4.14.1
urllib3==2.5.0
uvicorn==0.35.0
```

---

# ⚙️ Ejecución Local

## 🖥️ Ejecución Local

### 📁 Estructura del Repositorio

Este proyecto está alojado en:

**[https://github.com/Jonathan-1145/ai_inmobiliaria](https://github.com/Jonathan-1145/ai_inmobiliaria)**

El código fuente se encuentra en la carpeta raíz:

```
ai_inmobiliaria/
```

### 📦 Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Jonathan-1145/ai_inmobiliaria.git
cd ai_inmobiliaria
```

### 🧠 Paso 2: Descargar el Modelo y Ubicarlo

1. Crea la carpeta `backend/models/` si no existe:

```bash
mkdir -p backend/models
```

2. Descarga el modelo Mistral utilizado:

   [⬇️ Descargar desde Hugging Face (Q4_K_M)](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf)
3. Guarda el archivo `.gguf` en:

```
backend/models/
```

📌 **Importante:** Si usas un modelo distinto, ajusta la siguiente línea en `local_tests/main_local.py`:

```python
MODEL_PATH = "backend/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
```

### ⚙️ Paso 3: Crear y Activar el Entorno Virtual

#### 🪟 Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

#### 🐧 Linux / 🍎 macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 📥 Paso 4: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 🔐 Paso 5: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
DB_NAME=nombre_basededatos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=clave_secreta
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_basededatos
API_SECRET=tu_api_token
WEB_API_SECRET=tu_web_token
APP_RAM_GB=8
LOG_LEVEL=DEBUG
```

⚠️ **NO INCLUYAS:** `MODEL_PATH`, `PROMPT_PATH`, `MODEL_DIR`, `PROMPT_DIR` (ya están definidos en `main_local.py`).

### 🧱 Paso 6: Base de Datos Requerida (PostgreSQL)

Tu instancia de PostgreSQL debe tener tres tablas con los siguientes esquemas:

#### 📌 Tabla `inmueble`

* `titulo`, `slug`, `descripcion`, `descripcion_corta`
* `tipo`, `precio`, `ubicacion`, `barrio`, `ciudad`
* `area_m2`, `habitaciones`, `banos`, `carros`
* `estado`, `fecha_publicacion`, `usuario_id`

#### 📌 Tabla `mapa_inmuebles`

* `latitud`, `longitud`, `inmueble_id`

#### 📌 Tabla `imagenes_inmuebles`

* `imagen`, `url_imagen`, `orden`, `inmueble_id`

⚠️ Deben coincidir exactamente con los modelos esperados por el sistema.

### 🚀 Paso 7: Iniciar la App en Modo Local

#### 🪟 Windows (PowerShell)

```powershell
uvicorn local_tests.main_local:app --host 0.0.0.0 --port 8000 --reload
```

#### 🐧 Linux / 🍎 macOS

```bash
uvicorn local_tests.main_local:app --host 0.0.0.0 --port 8000 --reload
```

La aplicación quedará disponible en:

```
http://localhost:8000
```

### 🛠️ Comandos Útiles (Solo con Web Token Válido)

🔄 **Resetear sesión manualmente:**

```bash
curl -X POST "http://127.0.0.1:8000/reset-memory" \
     -H "Authorization: Bearer web_api_secret" \
     -H "Content-Type: application/json"
```

---

# 🧪 Pruebas y Tests (Falta por realizar más tests y actualizar este apartado)

Este proyecto cuenta con un entorno de pruebas robusto utilizando `pytest`, `coverage.py`, fixtures y una base de datos SQLite en memoria con datos precargados. Las pruebas están organizadas para permitir validación de componentes individuales y pruebas de integración simples.

## ▶️ Ejecución local de pruebas

1. Instala las dependencias necesarias:

```
pip install pytest coverage
```

2. Ejecuta los tests:

```
pytest
```

3. Opcionalmente, obtén un reporte de cobertura de código:

```
coverage run -m pytest
coverage report -m
```

## 🪨 Arquitectura General

```
| -- local_tests

    | -- main_local.py

    | -- test_mistral.py

| -- tests

    | -- assets

        | -- test_data.sql

    | -- utils

        | -- conftest.py

        | -- db_setup.py

    | -- test_concurrency.py
```

## 🧪 Base de datos de pruebas

Se utiliza una base de datos temporal en disco, generada en tiempo de ejecución con SQLite.

El archivo [`test_data.sql`](tests/assets/test_data.sql) define:

* Tablas: `inmueble`, `imagenes_inmuebles`, `mapa_inmuebles`
* Datos de prueba precargados (1 inmueble, imágenes y coordenadas)

El módulo [`db_setup.py`]() crea esta base de datos, carga el SQL y expone una sesión lista para usarse en pruebas mediante `pytest`.

```
@pytest.fixture
def temp_db():
    # Devuelve una sesión conectada a un .db temporal cargado desde test_data.sql
```

Esto permite ejecutar pruebas con datos reales sin afectar el entorno de producción ni requerir servicios externos.

## 🔧 Variables de entorno

El archivo [`conftest.py`]() establece el entorno de pruebas, forzando el uso de una base de datos SQLite en memoria mediante:

```
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
```

## 🧪 Simulaciones locales

Las pruebas en `local_tests/` permiten simular ejecuciones E2E sin necesidad de orquestación externa o despliegue completo.

Se usan principalmente para validar respuestas del modelo y verificar consistencia de la salida.

Para más información sobre cómo ejecutar pruebas de forma manual, consulta la sección [⚙️ Ejecución Local](https://github.com/Jonathan-1145/ai_inmobiliaria?tab=readme-ov-file#%EF%B8%8F-ejecuci%C3%B3n-local).

---

## 🛡️ Resumen Técnico Final

* ✅ IA local eficiente con minimización de alucinaciones mediante prompting controlado y filtros semánticos.
* ✅ Confirmaciones realistas y robustas.
* ✅ Prompting realista y profesional.
* ✅ Memoria de sesión eficiente y modular.
* ✅ Código listo para despliegue.
* ✅ Interfaz responsiva y bien diseñada.
* ✅ Seguridad por token en headers.
* ✅ Test coverage y arquitectura modular.

> HomeCat representa una implementación moderna y responsable de IA conversacional con datos estructurados, orientado a la experiencia del usuario y al cumplimiento riguroso de objetivos reales en contextos inmobiliarios.

---

## 📝 Licencia

Este proyecto forma parte de un portafolio profesional y no está licenciado para uso comercial sin autorización previa. Puedes examinar el código y adaptarlo con fines educativos o de inspiración técnica, siempre con atribución.

---

## 📫 Contacto

**Jonathan Libreros Cardona**

Estudiante de Ingeniería de Datos e Inteligencia Artificial

Estudiante de Tecnología en Análisis y Desarrollo de Software

GitHub: [@Jonathan-1145](https://github.com/Jonathan-1145)

Correo: jonathanlibrerosc1145@gmail.com
