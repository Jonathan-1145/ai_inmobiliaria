from backend.logger_setup import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

# Estructura para petición de mensaje al chatbot
class ChatRequest(BaseModel):
    session_id: str
    message: str

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug("📥 ChatRequest recibida", extra={"data": data})


# Estructura de respuesta del chatbot
class ChatResponse(BaseModel):
    response: str

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug("📤 ChatResponse generada", extra={"data": data})
