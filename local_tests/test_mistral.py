from llama_cpp import Llama
import os

MODEL_PATH = "backend/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

PROMPT = """
<<SYS>>
Eres un asesor inmobiliario inteligente, amable y profesional. Ayudas a los usuarios a encontrar propiedades reales según sus necesidades.
<</SYS>>

user: Hola
assistant:
""".strip()

def main():
    print("[INFO] 🚀 Cargando modelo para prueba...")
    model = Llama(
        model_path=MODEL_PATH,
        n_ctx=4096,
        n_threads=8,
        n_gpu_layers=0,
        use_mlock=True,
        use_mmap=True,
        verbose=False
    )

    print("[INFO] ✅ Modelo cargado. Ejecutando inferencia...\n")

    output = model(
        prompt=PROMPT,
        max_tokens=256,
        temperature=0.4,
        top_p=0.85,
        top_k=30,
        repeat_penalty=1.2,
        stop=["Usuario:", "Asesor:", "<</SYS>>"]
    )

    respuesta = output["choices"][0]["text"].strip()
    print("== Respuesta generada ==\n")
    print(respuesta)

if __name__ == "__main__":
    main()
