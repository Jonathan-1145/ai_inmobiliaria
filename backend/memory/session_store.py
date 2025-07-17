# Placeholder para futuro almacenamiento persistente (base de datos, archivo, etc.)

class SessionStore:
    """
    Clase opcional pensada para almacenar sesiones en disco o base de datos.
    Actualmente no está implementada.
    """
    def save_session(self, session_id: str, history: list[dict]):
        pass  # TODO: Implementar guardado persistente

    def load_session(self, session_id: str) -> list[dict]:
        return []  # TODO: Implementar carga persistente

    def delete_session(self, session_id: str):
        pass  # TODO: Implementar eliminación persistente
