from backend.api.utils.auth_utils import verificar_token_web
from fastapi import APIRouter, Depends, Query, Request
from backend.db.crud.property import search_properties
from backend.db.schemas.property import InmuebleOut
from backend.api.chat import router as chat_router
from backend.db.models.property import Inmueble
from backend.logger_setup import get_logger
from fastapi.responses import JSONResponse
from backend.db.database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
logger = get_logger(__name__)
router = APIRouter()
router.include_router(chat_router)

@router.get("/status", dependencies=[Depends(verificar_token_web)])
def status(request: Request):
    """
    Verifica el estado de la API.
    """
    logger.info("✔️ Endpoint /status consultado")
    return {
        "status": "IA Inmobiliaria activa",
        "modelo": "Mistral 7B Instruct V0.2 Q4 K M",
        "fuente": getattr(request.app.state.llm, "model_path", "N/A")
    }

@router.post("/session/reset", dependencies=[Depends(verificar_token_web)])
async def reset_session(session_id: str = Query(...), request: Request = None):
    """
    Reinicia la sesión del usuario (borra historial y filtros).
    Útil para pruebas manuales durante desarrollo.
    """
    memory = request.app.state.memory
    memory.reset_session(session_id)
    return JSONResponse(content={"status": "reset_ok", "session_id": session_id})

@router.get("/debug/info", dependencies=[Depends(verificar_token_web)])
async def debug_info(request: Request, db: Session = Depends(get_db)):
    llm = request.app.state.llm
    memory = request.app.state.memory

    info = {
        "modelo_cargado": llm is not None,
        "modelo_path": getattr(llm, "model_path", "N/A"),
        "prompt_path": getattr(llm, "prompt_path", "N/A"),
        "sesiones_activas": len(memory.histories),
        "filtros_por_sesion": len(memory.filters),
        "propiedades_cargadas": db.query(Inmueble).count()
    }

    logger.debug("🔍 Endpoint /debug/info consultado", extra=info)
    return info

@router.get("/buscar", response_model=List[InmuebleOut], dependencies=[Depends(verificar_token_web)])
def buscar_propiedades(
    ciudad: Optional[str] = Query(None),
    barrio: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    precio_max: Optional[float] = Query(None),
    habitaciones: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    logger.info("🔎 Búsqueda ejecutada", extra={
        "ciudad": ciudad,
        "barrio": barrio,
        "tipo": tipo,
        "precio_max": precio_max,
        "habitaciones": habitaciones,
        "limit": limit,
        "offset": offset
    })

    return search_properties(
        db,
        ciudad=ciudad,
        barrio=barrio,
        tipo=tipo,
        precio_max=precio_max,
        habitaciones=habitaciones,
        limit=limit,
        offset=offset
    )

@router.get("/health", dependencies=[Depends(verificar_token_web)])
async def health_check():
    logger.debug("✅ Endpoint /health revisado")
    return {"status": "ok"}