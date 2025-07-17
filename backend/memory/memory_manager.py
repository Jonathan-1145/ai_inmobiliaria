import threading
from backend.logger_setup import get_logger
import datetime

logger = get_logger(__name__)

MAX_HISTORY_LENGTH = 20

class MemoryManager:
    """
    Maneja la memoria conversacional, filtros y estado por sesión.
    Ahora es thread-safe gracias a locking interno.
    """
    def __init__(self):
        self.sessions = {}
        self.lock = threading.RLock()
        logger.info("🧠 MemoryManager inicializado (instancia global)")

    def _ensure_session(self, session_id: str):
        logger.debug(f"🔒 Verificando existencia de sesión: {session_id}")
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "history": [],
                    "filters": {
                        "tipo": None,
                        "precio": None,
                        "barrio": None,
                        "ciudad": None,
                        "area_m2": None,
                        "habitaciones": None,
                        "banos": None,
                        "carros": None
                    },
                    "state": "default",
                    "flags": {
                        "filtros_completos": False,
                        "mostrar_propiedad": False
                    },
                    "last_activity": datetime.datetime.now(datetime.timezone.utc)
                }
                logger.info(f"🆕 Sesión creada: {session_id}")
            else:
                logger.debug(f"✅ Sesión existente: {session_id}")

    def get_history(self, session_id: str) -> list[dict]:
        logger.debug(f"📥 get_history llamado para sesión: {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            history = list(self.sessions[session_id]["history"])
            logger.debug(f"📜 Historial obtenido para sesión {session_id}, {len(history)} mensajes")
            self.update_activity(session_id)
            return history

    def add_message(self, session_id: str, role: str, message: str):
        logger.debug(f"➕ Agregando mensaje a sesión {session_id} - Rol: {role}")
        with self.lock:
            self._ensure_session(session_id)
            history = self.sessions[session_id]["history"]
            history.append({"role": role, "content": message})

            if len(history) > MAX_HISTORY_LENGTH:
                self.sessions[session_id]["history"] = history[-MAX_HISTORY_LENGTH:]
                logger.debug(f"📉 Historial truncado a {MAX_HISTORY_LENGTH} mensajes en sesión {session_id}")

            self.update_activity(session_id)
            logger.info(f"✉️ Mensaje agregado en sesión {session_id} por {role}")

    def clear_session(self, session_id: str):
        logger.debug(f"🗑️ clear_session llamado para: {session_id}")
        with self.lock:
            existed = self.sessions.pop(session_id, None)
            if existed:
                logger.info(f"🗑️ Sesión eliminada: {session_id}")
            else:
                logger.warning(f"⚠️ Intento de eliminar sesión inexistente: {session_id}")
            self.update_activity(session_id)

    def update_activity(self, session_id: str):
        with self.lock:
            self._ensure_session(session_id)
            self.sessions[session_id]["last_activity"] = datetime.datetime.now(datetime.timezone.utc)
            logger.debug(f"🕒 Actividad actualizada para sesión {session_id}")

    def get_last_activity(self, session_id: str):
        with self.lock:
            self._ensure_session(session_id)
            return self.sessions[session_id].get("last_activity")

    def get_all_sessions(self):
        with self.lock:
            return list(self.sessions.keys())

    # === Filtros ===
    def get_filters(self, session_id: str) -> dict:
        logger.debug(f"📥 get_filters llamado para sesión: {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            filters = self.sessions[session_id]["filters"].copy()
            logger.debug(f"🔍 Filtros obtenidos para sesión {session_id}: {filters}")
            return filters

    def update_filter(self, session_id: str, key: str, value):
        logger.debug(f"🔧 update_filter llamado: {key} = {value} en sesión {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            if key in self.sessions[session_id]["filters"]:
                self.sessions[session_id]["filters"][key] = value
                logger.info(f"🛠️ Filtro '{key}' actualizado en sesión {session_id} a {value}")

    def update_filters(self, session_id: str, new_data: dict):
        logger.debug(f"🔧 update_filters llamado para sesión {session_id}: {new_data}")
        with self.lock:
            self._ensure_session(session_id)
            for key, value in new_data.items():
                if key in self.sessions[session_id]["filters"] and value is not None:
                    self.sessions[session_id]["filters"][key] = value
                    logger.info(f"🛠️ Filtro '{key}' actualizado en sesión {session_id} a {value}")

    def clear_filters(self, session_id: str):
        logger.debug(f"🧽 clear_filters llamado para sesión: {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            for key in self.sessions[session_id]["filters"]:
                self.sessions[session_id]["filters"][key] = None
            logger.info(f"🧹 Filtros limpiados en sesión {session_id}")

    # === Estado ===
    def get_state(self, session_id: str):
        logger.debug(f"📥 get_state llamado para sesión: {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            state = self.sessions[session_id].get("state", "default")
            logger.debug(f"🎯 Estado obtenido para sesión {session_id}: {state}")
            return state

    def set_state(self, session_id: str, state: str):
        logger.debug(f"🔄 set_state llamado: '{state}' para sesión {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            self.sessions[session_id]["state"] = state
            logger.info(f"🔄 Estado cambiado a '{state}' en sesión {session_id}")

    # === Flags ===
    def get_flags(self, session_id: str) -> dict:
        logger.debug(f"📥 get_flags llamado para sesión: {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            flags = self.sessions[session_id]["flags"].copy()
            logger.debug(f"🏷️ Flags obtenidas para sesión {session_id}: {flags}")
            return flags

    def set_flag(self, session_id: str, key: str, value: bool):
        logger.debug(f"🏁 set_flag llamado: {key} = {value} en sesión {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            self.sessions[session_id]["flags"][key] = value
            logger.info(f"🏷️ Flag '{key}' establecida en {value} para sesión {session_id}")

    def clear_flags(self, session_id: str):
        logger.debug(f"🧽 clear_flags llamado para sesión: {session_id}")
        with self.lock:
            self._ensure_session(session_id)
            self.sessions[session_id]["flags"] = {
                "filtros_completos": False,
                "mostrar_propiedad": False
            }
            logger.info(f"🧹 Flags limpiadas en sesión {session_id}")
