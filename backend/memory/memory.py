from backend.memory.memory_manager import MemoryManager
from backend.logger_setup import get_logger

logger = get_logger(__name__)

# Instancia global de memoria para ser usada por toda la app
memory = MemoryManager()
logger.info("🧠 MemoryManager inicializado (instancia global)")