from backend.api.utils.confirmation_utils import es_confirmacion_usuario
from backend.api.utils.llm_prompt import build_prompt
from backend.logger_setup import get_logger
from dotenv import load_dotenv
from llama_cpp import Llama
import multiprocessing
import traceback
import asyncio
import time
import sys
import os
import re

logger = get_logger(__name__)

load_dotenv()

class LLMEngine:
    def __init__(self, model_path: str, prompt_template_path: str):
        try:
            model_name = os.path.basename(model_path).lower()
            total_cores = multiprocessing.cpu_count()

            # === Configuración dinámica basada en el modelo detectado ===
            if "tinyllama" in model_name:
                n_threads = min(total_cores, 16)
                n_ctx = 2048
            elif "mistral" in model_name:
                n_threads = min(total_cores, 16)
                n_ctx = 4096
            elif "llama3-8b" in model_name:
                n_threads = min(total_cores, 24)
                n_ctx = 8192
            elif "llama3-70b" in model_name:
                n_threads = min(total_cores, 32)
                n_ctx = 32768
            else:
                n_threads = min(total_cores, 16)
                n_ctx = 4096

            n_gpu_layers = int(os.getenv("LLAMA_GPU_LAYERS", 0))

            logger.info("🔧 Configuración del modelo:")
            logger.info(f"  - Modelo detectado: {model_name}")
            logger.info(f"  - n_ctx: {n_ctx}")
            logger.info(f"  - n_threads: {n_threads}")
            logger.info(f"  - n_gpu_layers: {n_gpu_layers}")
            logger.info(f"🖥️  Núcleos disponibles: {total_cores}")
            logger.info("⚠️ Ejecutando en CPU" if n_gpu_layers == 0 else "⚙️ Ejecutando con capas en GPU")

            # === Inicialización segura del modelo ===
            self.model = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                use_mlock=True,
                use_mmap=True,
                low_vram=False,
                verbose=False
            )

            logger.debug("✅ Modelo instanciado correctamente")

        except Exception as e:
            logger.error(f"❌ Fallo al cargar el modelo: {e}", exc_info=True)
            raise

        if not os.path.exists(prompt_template_path):
            raise FileNotFoundError(f"Prompt no encontrado en: {prompt_template_path}")

        with open(prompt_template_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    async def chat(self, user_input: str, history: list[dict]) -> str:
        prompt = build_prompt(user_input, history, self.prompt_template)

        # === Detección robusta de intención: regex + embeddings ===
        hay_confirmacion = es_confirmacion_usuario(user_input)
        hay_filtros = any("estos son los datos reales" in m["content"].lower() for m in history if m["role"] == "system")

        # === Ajuste adaptativo de max_tokens ===
        if hay_confirmacion or hay_filtros:
            max_tokens = 768
        else:
            user_chars = len(user_input)
            max_tokens = 512 if user_chars < 200 else 768 if user_chars < 500 else 1024

        # === Hiperparámetros calibrados para velocidad y coherencia ===
        temperature = 0.4
        top_p = 0.85
        top_k = 30
        repeat_penalty = 1.2
        frequency_penalty = 0.3
        stop = ["Usuario:", "Asesor:", "<</SYS>>", "\nUsuario", "\nAsesor", "Sistema:", "\nSistema", "System:", "\nSystem"]

        logger.debug("🚦 Parámetros de inferencia:")
        logger.debug(f"         - Confirmación detectada: {hay_confirmacion}")
        logger.debug(f"         - max_tokens: {max_tokens}")
        logger.debug(f"         - temperature: {temperature}, top_p: {top_p}, top_k: {top_k}")
        logger.debug(f"         - repeat_penalty: {repeat_penalty}, frequency_penalty: {frequency_penalty}")

        try:
            start_time = time.perf_counter()

            output = await asyncio.to_thread(
                self.model,
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                frequency_penalty=frequency_penalty,
                stop=stop
            )

            elapsed = time.perf_counter() - start_time
            logger.info(f"🕒 Tiempo de inferencia: {elapsed:.2f} segundos")

            choices = output.get("choices", [])
            if not choices or not isinstance(choices, list) or "text" not in choices[0]:
                raise ValueError("La respuesta del modelo no contiene texto válido")

            response = choices[0]["text"].strip()
            response = re.sub(r"(?:^|[\r\n]+)(Sistema:|Asesor:|Usuario:|System:)\s*", "", response, flags=re.IGNORECASE)
            if not response:
                raise ValueError("Texto de respuesta vacío")

            return response

        except Exception as e:
            logger.error(f"Durante inferencia: {e}", exc_info=True)
            return "Hubo un problema generando la respuesta. Estoy organizando la información y en breve te mostraré las opciones disponibles."
