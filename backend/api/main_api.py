from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, Request, HTTPException, Depends
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from backend.logger_setup import get_logger
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import datetime
from mimetypes import guess_type
from dotenv import load_dotenv
import asyncio
import glob
import os

from backend.api.utils.auth_utils import verificar_token_web
from backend.api.routes import router

load_dotenv()
API_SECRET = os.getenv("API_SECRET")

logger = get_logger(__name__)
logger.info("📡 Iniciando FastAPI")

# Detectar modelo y prompt automáticamente
def detectar_modelo_y_prompt():
    modelo_dir = os.getenv("MODEL_DIR", "/data/storage/models")
    prompt_dir = os.getenv("PROMPT_DIR", "/data/storage/prompts")

    modelos = glob.glob(os.path.join(modelo_dir, "*.gguf"))
    prompts = glob.glob(os.path.join(prompt_dir, "*.txt"))

    if not modelos:
        raise FileNotFoundError(f"No se encontraron modelos .gguf en {modelo_dir}")
    if not prompts:
        raise FileNotFoundError(f"No se encontraron prompts .txt en {prompt_dir}")

    logger.info(f"Modelo detectado: {modelos[0]}")
    logger.info(f"Prompt detectado: {prompts[0]}")
    return modelos[0], prompts[0]

async def idle_loop():
    while True:
        await asyncio.sleep(60)

# Lógica de ciclo de vida (inicialización)
@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.llm_engine.llm_engine import LLMEngine
    from backend.memory.memory import MemoryManager
    from backend.api import chat

    logger.info("🚀 Inicializando modelo en entorno de producción")

    try:
        model_path = os.getenv("MODEL_PATH")
        prompt_path = os.getenv("PROMPT_PATH")

        if not model_path or not prompt_path:
            logger.warning("Rutas no definidas en .env. Intentando detectar automáticamente...")
            model_path, prompt_path = detectar_modelo_y_prompt()

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo no encontrado en {model_path}")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt no encontrado en {prompt_path}")

        app.state.llm = LLMEngine(model_path, prompt_path)
        app.state.memory = MemoryManager()

        # Se enlaza al módulo de chat
        chat.llm = app.state.llm
        chat.model_loaded = True

        asyncio.create_task(auto_reset_sessions(app))

        logger.info("✅ Modelo y memoria cargados correctamente")

        dummy_prompt = "Hola, ¿puedes ayudarme a buscar un apartamento?"
        dummy_history = [{"role": "system", "content": "Eres un asistente inmobiliario."}]
        logger.info("🔥 Ejecutando inferencia de calentamiento...")
        response = await app.state.llm.chat(dummy_prompt, dummy_history)
        logger.info(f"✅ Warm-up completado con respuesta: {response[:50]}...")
    except Exception as e:
        logger.error("❌ Fallo al inicializar", exc_info=True)
        logger.warning("⚠️ Fallo el warm-up", exc_info=True)

    yield

    logger.info("🛑 Cerrando servidor...")

# Static y templates
class CustomStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        full_path, stat_result = self.lookup_path(path)
        if stat_result is None:
            return await super().get_response(path, scope)

        content_type, _ = guess_type(full_path)
        if full_path.endswith(".js"):
            content_type = "application/javascript"
        elif full_path.endswith(".css"):
            content_type = "text/css"

        return FileResponse(full_path, stat_result=stat_result, media_type=content_type)
    
# Instanciación de la app
app = FastAPI(lifespan=lifespan)

# Registro de rutas
app.include_router(router)

# Middleware para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (custom handling for JS, CSS)
app.mount("/static", CustomStaticFiles(directory="frontend/static"), name="static")

templates = Jinja2Templates(directory="frontend/templates")
    
@app.get("/token/onlyjs", dependencies=[Depends(verificar_token_web)])
async def get_token_for_js():
    """
    Devuelve ambos tokens, pero solo si el frontend lo solicita con el webToken correcto.
    Evita que se exponga en HTML directamente.
    """
    api_token = os.getenv("API_SECRET", "api-dev-token")
    web_token = os.getenv("WEB_API_SECRET", "web-dev-token")

    return {
        "apiToken": api_token,
        "webToken": web_token
    }

@app.get("/start", response_class=HTMLResponse)
async def start_page():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Cargando HomeCat...</title>
        <script>
            let dots = 0;
            const intervalId = setInterval(() => {
                dots = (dots + 1) % 4;
                document.title = "Cargando HomeCat" + ".".repeat(dots);
            }, 500);
        </script>
        <link rel="icon" href="/static/img/favicon.ico" type="image/ico" />
        <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
        <style>
            body {
                background-color: #121212;
                font-family: 'Inter', sans-serif;
                color: #e0e0e0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                user-select: none;
                -webkit-user-select: none;
                -ms-user-select: none;
                -moz-user-select: none;
            }
            
            ::selection {
                background: transparent;
            }

            .pulse-container {
                display: flex;
                gap: 8px;
                margin-bottom: 20px;
            }

            .pulse-bar {
                width: 6px;
                height: 30px;
                background: #58a6ff;
                border-radius: 3px;
                animation: pulse 1s infinite ease-in-out;
            }

            .pulse-bar:nth-child(1) { animation-delay: 0s; }
            .pulse-bar:nth-child(2) { animation-delay: 0.2s; }
            .pulse-bar:nth-child(3) { animation-delay: 0.4s; }
            .pulse-bar:nth-child(4) { animation-delay: 0.6s; }
            .pulse-bar:nth-child(5) { animation-delay: 0.8s; }

            @keyframes pulse {
                0%, 100% { transform: scaleY(0.4); opacity: 0.5; }
                50% { transform: scaleY(1.2); opacity: 1; }
            }

            p {
                font-size: 1.1rem;
                color: #a0a0a0;
                animation: fadeIn 1s ease-in;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="pulse-container">
            <div class="pulse-bar"></div>
            <div class="pulse-bar"></div>
            <div class="pulse-bar"></div>
            <div class="pulse-bar"></div>
            <div class="pulse-bar"></div>
        </div>
        <p>Preparando HomeCat...</p>

        <script>
        const delay = ms => new Promise(res => setTimeout(res, ms));

        fetch("/get-token")
            .then(res => res.headers.get("X-Web-Authorization-Token"))
            .then(async token => {
                if (!token) throw new Error("Token no recibido");

                await delay(3000);

                sessionStorage.setItem("webToken", token);

                return fetch("/", {
                    headers: { "Authorization": "Bearer " + token }
                });
            })
            .then(res => {
                if (!res.ok) throw new Error("No autorizado al acceder a '/'");
                return res.text();
            })
            .then(html => {
                clearInterval(intervalId);
                document.open();
                document.write(html);
                document.close();
                document.title = "HomeCat";
            })
            .catch(err => {
                document.body.innerHTML = "<h2>❌ Error cargando HomeCat</h2><pre style='color:#ff7b72'>" + err + "</pre>";
            });
        </script>

        <script>                    
            document.addEventListener('contextmenu', event => event.preventDefault());
                        
            document.addEventListener('copy', event => event.preventDefault());
            document.addEventListener('cut', event => event.preventDefault());
            document.addEventListener('keydown', function(e) {
                
                if ((e.ctrlKey && ['c', 'x', 'u', 's'].includes(e.key.toLowerCase())) ||
                    (e.ctrlKey && e.shiftKey && ['i', 'j'].includes(e.key.toLowerCase())) ||
                    e.key === 'F12') {
                    e.preventDefault();
                }
            });
        </script>                
    </body>
    </html>
    """)

security = HTTPBearer(auto_error=False)

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not credentials:
        return RedirectResponse("/start", status_code=307)

    request.headers.__dict__["_list"].append(
        (b"authorization", f"Bearer {credentials.credentials}".encode())
    )

    try:
        await verificar_token_web(request)
    except HTTPException:
        return RedirectResponse("/start", status_code=307)

    return templates.TemplateResponse("index.html", {"request": request})

# Handler genérico para errores HTTP comunes
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    status_code = exc.status_code

    if status_code in {400, 401, 403, 404, 405, 409, 500, 502, 504}:
        template_name = f"{status_code}.html"
    else:
        template_name = "500.html"

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "status_code": status_code,
            "error_detail": exc.detail
        },
        status_code=status_code
    )

# Handler específico para 422 Unprocessable Entity (error de validación con Pydantic)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(
        "422.html",
        {
            "request": request,
            "status_code": 422,
            "errors": exc.errors()
        },
        status_code=422
    )

# Handler genérico para las excepciones no controladas
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Excepción no controlada: {exc}", exc_info=True)
    return templates.TemplateResponse(
        "500.html",
        {"request": request, "status_code": 500, "error_detail": str(exc)},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR
    )

@app.get("/get-token")
async def get_token(request: Request):
    api_token = os.getenv("API_SECRET", "api-dev-token")
    web_token = os.getenv("WEB_API_SECRET", "web-dev-token")

    response = JSONResponse(content={"message": "Tokens enviados"})
    response.headers["X-Authorization-Token"] = api_token
    response.headers["X-Web-Authorization-Token"] = web_token
    return response

async def auto_reset_sessions(app):
    while True:
        await asyncio.sleep(600)  # Cada 10 minutos

        # Validación defensiva
        if not hasattr(app.state, "memory"):
            logger.warning("⚠️ No se encontró memory en app.state (¿no inicializada todavía?)")
            continue

        memory = app.state.memory
        sesiones = memory.get_all_sessions()

        for session_id in sesiones:
            last_activity = memory.get_last_activity(session_id)
            if last_activity and datetime.datetime.now(datetime.timezone.utc) - last_activity >= datetime.timedelta(hours=1):
                memory.reset_session(session_id)
                logger.info(f"🔄 Sesión {session_id} reseteada automáticamente.")
