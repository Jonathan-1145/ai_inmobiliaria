from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, Request, HTTPException, Depends
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from backend.logger_setup import get_logger
from contextlib import asynccontextmanager
import sys
import os

from backend.api.utils.auth_utils import verificar_token_web, verificar_token
from backend.memory.memory_manager import MemoryManager
from backend.llm_engine.llm_engine import LLMEngine
from backend.api.routes import router

# Configuración del logger
logger = get_logger(__name__)

# Establece el modo explícito de entorno
os.environ["ENV"] = "local"

MODEL_PATH = "backend/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
PROMPT_PATH = "backend/prompt/prompt_template.txt"

_llm_instance = None
_memory_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _llm_instance, _memory_instance

    logger.debug("🚀 Inicializando entorno...")

    try:
        if not _llm_instance:
            logger.info("🧠 Cargando modelo...")
            _llm_instance = LLMEngine(MODEL_PATH, PROMPT_PATH)
        else:
            logger.info("✅ Modelo ya estaba cargado")

        if not _memory_instance:
            logger.info("💾 Inicializando memoria...")
            _memory_instance = MemoryManager()
        else:
            logger.info("✅ Memoria ya estaba cargada")

        app.state.llm = _llm_instance
        app.state.memory = _memory_instance

        # === Warm-up ===
        dummy_prompt = "Hola, ¿puedes ayudarme a buscar un apartamento?"
        dummy_history = [{"role": "system", "content": "Eres un asistente inmobiliario."}]
        try:
            logger.info("🔥 Ejecutando inferencia de calentamiento (warm-up)...")
            response = await _llm_instance.chat(dummy_prompt, dummy_history)
            logger.info(f"✅ Warm-up completado con respuesta: {response[:60]}...")
        except Exception as e:
            logger.warning("⚠️ Fallo durante el warm-up", exc_info=True)

    except Exception as e:
        logger.error(f"❌ Error al cargar modelo/memoria: {e}", exc_info=True)
        raise e

    yield

    logger.debug("🛑 Cerrando entorno local (lifespan)")

# Crear la app de FastAPI con el contexto de vida
app = FastAPI(lifespan=lifespan)

# Carga del frontend
frontend_path = os.path.abspath("frontend")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(frontend_path, "templates"))

# Rutas principales
app.include_router(router)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    status_code = exc.status_code

    if status_code in {400, 401, 403, 404, 405, 409, 500, 502, 504}:
        template_name = f"{status_code}.html"
    else:
        template_name = "error.html"

    return templates.TemplateResponse(
        template_name,
        {"request": request, "status_code": status_code, "error_detail": exc.detail},
        status_code=status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(
        "422.html",
        {"request": request, "status_code": 422, "errors": exc.errors()},
        status_code=422
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Excepción no controlada: {exc}", exc_info=True)
    return templates.TemplateResponse(
        "500.html",
        {"request": request, "status_code": 500, "error_detail": str(exc)},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR
    )

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

@app.get("/health", dependencies=[Depends(verificar_token_web)])
async def health_check():
    logger.info("🩺 Estado de salud solicitado")
    return {"status": "ok"}

@app.post("/reset-memory", dependencies=[Depends(verificar_token_web)])
async def reset_memory():
    global _memory_instance
    _memory_instance = MemoryManager()
    app.state.memory = _memory_instance
    logger.warning("♻️ Memoria reiniciada manualmente")
    return {"message": "Memoria reiniciada"}

@app.get("/get-token")
async def get_token(request: Request):
    api_token = os.getenv("API_SECRET", "api-dev-token")
    web_token = os.getenv("WEB_API_SECRET", "web-dev-token")

    response = JSONResponse(content={"message": "Tokens enviados"})
    response.headers["X-Authorization-Token"] = api_token
    response.headers["X-Web-Authorization-Token"] = web_token
    return response

# Rutas de Prueba (Forzando Errores)
@app.get("/force-400")
async def force_400():
    raise HTTPException(status_code=400, detail="Solicitud incorrecta de prueba")

@app.get("/force-401", dependencies=[Depends(verificar_token)])
async def force_401():
    return {"ok": True}

@app.get("/force-403", dependencies=[Depends(verificar_token_web)])
async def force_403():
    return {"ok": True}

@app.get("/force-404")
async def force_404():
    raise HTTPException(status_code=404, detail="Ruta no encontrada")

@app.post("/force-405")
async def force_405_post():
    return {"ok": True}

@app.get("/force-409")
async def force_409():
    raise HTTPException(status_code=409, detail="Conflicto detectado")

@app.get("/force-422")
async def force_422(param: int):
    return {"param": param}

@app.get("/force-500")
async def force_500():
    raise Exception("Error interno del servidor")

@app.get("/force-502")
async def force_502():
    raise HTTPException(status_code=502, detail="Bad Gateway simulado")

@app.get("/force-504")
async def force_504():
    raise HTTPException(status_code=504, detail="Gateway Timeout simulado")