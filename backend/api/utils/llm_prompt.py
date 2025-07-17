from typing import List
import re

def limpiar_instrucciones_ocultas(texto: str) -> str:
    """
    Elimina cualquier texto entre paréntesis que parezca una instrucción (no frases del usuario).
    """
    return re.sub(r"\(([^()]*instrucción[^()]*)\)", "", texto, flags=re.IGNORECASE)

def limpiar_texto_parentesis(texto: str) -> str:
    """
    Elimina todo lo que esté entre paréntesis (incluyendo los paréntesis) del texto.
    """
    return re.sub(r"\([^)]*\)", "", texto).strip()

def limpiar_prefijo_llm(respuesta: str) -> str:
    """
    Elimina prefijos innecesarios al inicio de la respuesta como 'Usuario:', 'user:', etc.
    También elimina espacios iniciales y saltos de línea redundantes.
    """
    return re.sub(r"^(Usuario|Usuro|User|usuario|usuro|user|Usuarioa|Usuario:|User:|Usuro:)[\s:\-]*", "", respuesta.strip(), flags=re.IGNORECASE)

def build_prompt(user_input: str, history: List[dict], prompt_template: str, role_map: dict = None) -> str:
    if role_map is None:
        role_map = {"user": "Usuario", "assistant": "Asesor", "system": "Sistema"}

    recent_history = history[-6:]
    history_text = ""

    for item in recent_history:
        role_label = role_map.get(item["role"], item["role"].capitalize())

        clean_content = limpiar_instrucciones_ocultas(item["content"])

        if item["role"] == "assistant":
            clean_content = limpiar_texto_parentesis(clean_content)

        history_text += f"{role_label}: {clean_content.strip()}\n"

    prompt = (
        f"<<SYS>>\n"
        f"{prompt_template.strip()}\n"
        f"<</SYS>>\n\n"
        f"{history_text.strip()}\n"
        f"Usuario: {user_input.strip()}\n"
        f"Asesor:"
    )

    return prompt.strip()
