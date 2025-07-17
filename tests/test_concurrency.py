from backend.memory.memory_manager import MemoryManager
from random import randint, choice
from time import sleep
import threading
import pytest

# ==== Configuración ====
NUM_THREADS_PER_SESSION = 5
NUM_ITERATIONS_PER_THREAD = 100
SESSIONS = ["session_a", "session_b"]

FILTER_KEYS = [
    "tipo", "precio", "ubicacion", "barrio", "ciudad",
    "area_m2", "habitaciones", "banos", "carros"
]

# ==== Función concurrente para cada hilo ====
def simulate_user_behavior(memory_manager, session_id):
    for i in range(NUM_ITERATIONS_PER_THREAD):
        # Agregar mensaje
        role = "user" if i % 2 == 0 else "assistant"
        memory_manager.add_message(session_id, role, f"Mensaje {i} desde hilo {threading.current_thread().name}")

        # Modificar un filtro aleatorio
        key = choice(FILTER_KEYS)
        value = randint(1, 100)
        memory_manager.update_filter(session_id, key, value)

        # Simular retardo
        sleep(0.001)

# ==== Test Principal ====
def test_memory_manager_concurrency():
    mm = MemoryManager()
    threads = []

    # Crear hilos por cada sesión
    for session_id in SESSIONS:
        for _ in range(NUM_THREADS_PER_SESSION):
            t = threading.Thread(target=simulate_user_behavior, args=(mm, session_id))
            threads.append(t)
            t.start()

    # Esperar a que todos los hilos terminen
    for t in threads:
        t.join()

    # === Verificaciones ===
    for session_id in SESSIONS:
        history = mm.get_history(session_id)
        filters = mm.get_filters(session_id)

        # Se deberían haber generado exactamente NUM_THREADS_PER_SESSION * NUM_ITERATIONS_PER_THREAD mensajes
        expected_messages = NUM_THREADS_PER_SESSION * NUM_ITERATIONS_PER_THREAD
        assert len(history) == expected_messages, f"{session_id} tiene {len(history)} mensajes, esperábamos {expected_messages}"

        # Los filtros deben tener valores (no todos None)
        none_count = sum(1 for v in filters.values() if v is None)
        assert none_count < len(filters), f"{session_id} tiene todos los filtros en None, esperábamos al menos uno seteado"


# ==== Pytest marker para que se pueda lanzar solo este test ====
@pytest.mark.concurrency
def test_concurrency_wrapper():
    test_memory_manager_concurrency()
