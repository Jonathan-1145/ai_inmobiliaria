from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.api.filter_extractor import (
    extract_filters_from_text,
    filters_estan_completos,
    limpiar_si_invento_propiedad,
)
from backend.api.utils.confirmation_utils import (
    es_confirmacion_usuario_embeddings,
    es_confirmacion_por_regex,
    es_indiferencia_usuario_embeddings,
    SUGERENCIAS_FILTROS_FALTANTES
)
from backend.api.search_engine import buscar_propiedad_ideal
from backend.api.schemas import ChatRequest, ChatResponse
from backend.db.models.property import Inmueble
from backend.api.utils.auth_utils import verificar_token
from backend.api.utils.llm_prompt import limpiar_texto_parentesis, limpiar_prefijo_llm
from backend.db.database import get_db
from backend.logger_setup import get_logger
from sqlalchemy.orm import Session
from uuid import uuid4
from difflib import get_close_matches

logger = get_logger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_handler(
    data: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    token_validado: None = Depends(verificar_token)
):
    session_id = data.session_id or "default_session"
    logger.info("📩 POST /chat recibido", extra={"session_id": session_id, "mensaje": data.message})

    llm = request.app.state.llm
    memory = request.app.state.memory

    try:
        logger.debug("🔁 Obteniendo datos de sesión", extra={"session_id": session_id})
        history = memory.get_history(session_id)
        if not history:
            logger.debug("⏱ Primera interacción detectada. Inyectando historial simulado.", extra={"session_id": session_id})
            history.append({
                "role": "system",
                "content": (
                    "Eres un asesor inmobiliario profesional, empático y humano. "
                    "Tu trabajo es conversar de forma natural para entender las necesidades del usuario. "
                    "No puedes mostrar propiedades hasta que el sistema te las entregue explícitamente. "
                    "No inventes información, no hagas promesas implícitas ni digas frases como 'estoy buscando'. "
                    "Adáptate al tono del usuario y mantén una conversación fluida, útil y realista."
                )
            })

        filtros_actuales = memory.get_filters(session_id)
        flags = memory.get_flags(session_id)

        logger.debug("🧪 Extrayendo filtros del mensaje", extra={"session_id": session_id})
        nuevos_filtros = extract_filters_from_text(data.message, db, filtros_actuales)

        if nuevos_filtros:
            logger.debug("🆕 Nuevos filtros detectados", extra={"session_id": session_id, "nuevos_filtros": nuevos_filtros})
            memory.update_filters(session_id, nuevos_filtros)
            filtros_actuales = memory.get_filters(session_id)

        filtros_completos = filters_estan_completos(filtros_actuales)
        logger.debug("📋 ¿Filtros completos?", extra={"session_id": session_id, "completos": filtros_completos})
        memory.set_flag(session_id, "filtros_completos", filtros_completos)

        try:
            if es_confirmacion_usuario_embeddings(data.message):
                logger.info("✅ Confirmación detectada por embeddings", extra={"session_id": session_id})
                memory.set_flag(session_id, "mostrar_propiedad", True)
                flags["mostrar_propiedad"] = True
            elif es_confirmacion_por_regex(data.message):
                logger.info("✅ Confirmación detectada por regex", extra={"session_id": session_id})
                memory.set_flag(session_id, "mostrar_propiedad", True)
                flags["mostrar_propiedad"] = True
        except Exception:
            logger.warning("⚠️ Error evaluando confirmación del usuario", exc_info=True, extra={"session_id": session_id})

        if flags.get("mostrar_propiedad"):
            if filtros_completos:
                logger.info("🔍 Buscando propiedad ideal", extra={"session_id": session_id, "filtros": filtros_actuales})
                propiedad = buscar_propiedad_ideal(db, filtros_actuales)

                if propiedad:
                    logger.info("🏡 Propiedad encontrada", extra={"session_id": session_id, "titulo": propiedad.titulo})

                    resumen = (
                        f"Nombre: {propiedad.titulo}\n"
                        f"Ciudad: {propiedad.ciudad}\n"
                        f"Barrio: {propiedad.barrio}\n"
                        f"Precio: ${int(propiedad.precio):,}\n"
                        f"Tipo: {propiedad.tipo}\n"
                        f"Área: {propiedad.area_m2} m²\n"
                        f"Habitaciones: {propiedad.habitaciones}\n"
                        f"Baños: {propiedad.banos}\n"
                        f"Parqueaderos: {propiedad.carros}"
                    )

                    history.append({
                        "role": "system",
                        "content": (
                            f"Estos son los datos REALES de la propiedad más adecuada según lo que pidió el usuario:\n"
                            f"{resumen}\n"
                            f"Redacta una respuesta natural, cálida y profesional como asesor humano, "
                            f"sin inventar nada. Incluye el nombre exacto de la propiedad. No repitas barrio y ciudad innecesariamente."
                        )
                    })

                    logger.debug("🧠 Llamando al modelo con resumen real", extra={"session_id": session_id})
                    model_response = await llm.chat(data.message, history)

                    if propiedad.slug and propiedad.imagenes:
                        imagenes = [img.url_imagen for img in propiedad.imagenes[:3] if img.url_imagen]
                        if imagenes:
                            url = f"https://multihabitat.lat/inmueble/{propiedad.slug}/"
                            group_id = uuid4().hex
                            imagenes_html = "".join([
                                f'<img src="{img}" data-full="{img}" data-group="{group_id}" loading="lazy" class="zoomable-img" '
                                f'style="width: 120px; max-width: 100%; border-radius: 10px; '
                                f'margin-right: 0.5rem; margin-bottom: 0.5rem; cursor: zoom-in;" alt="{propiedad.titulo}">'
                                for img in imagenes
                            ])
                            model_response += (
                                f"<div style='display: flex; flex-wrap: wrap; margin-top: 0.25rem; margin-bottom: 0.5rem;'>"
                                f"{imagenes_html}</div>"
                                f"<a href='{url}' target='_blank' "
                                f"style='display: inline-flex; align-items: center; gap: 0.4rem; color: #0d6efd; "
                                f"text-decoration: none; font-weight: 500;'>"
                                f"<i class='bi bi-box-arrow-up-right'></i> Ver esta propiedad en Multihabitat</a>"
                            )

                    memory.set_flag(session_id, "mostrar_propiedad", False)
                    memory.add_message(session_id, "user", data.message)
                    memory.add_message(session_id, "assistant", model_response)
                    logger.info("📤 Respuesta generada con propiedad", extra={"session_id": session_id})
                    model_response = limpiar_texto_parentesis(model_response)
                    model_response = limpiar_prefijo_llm(model_response)
                    return ChatResponse(response=model_response)
                else:
                    # Detectó intención de ver pero no hay datos completos
                    logger.info("❗ El usuario quiere ver propiedades pero faltan filtros", extra={"session_id": session_id})

                    campos_requeridos = ["tipo", "ciudad", "barrio", "habitaciones", "banos", "area_m2"]
                    campos_faltantes = [campo for campo in campos_requeridos if filtros_actuales.get(campo) in [None, "", -1]]

                    # Revisión por indiferencia
                    if es_indiferencia_usuario_embeddings(data.message):
                        logger.info("🙃 Usuario expresó indiferencia al elegir filtros", extra={"session_id": session_id})
                        for campo in campos_faltantes:
                            memory.update_filter(session_id, campo, "no importa")
                        filtros_actualizados = memory.get_filters(session_id)
                        memory.set_flag(session_id, "filtros_completos", filters_estan_completos(filtros_actualizados))
                        # Reintentar flujo normal en próxima llamada
                    else:
                        campo = campos_faltantes[0] if campos_faltantes else None
                        sugerencia = SUGERENCIAS_FILTROS_FALTANTES.get(
                            campo, "¿Podrías darme un poco más de información para ayudarte mejor?"
                        )

                        respuesta = (
                            "¡Estoy casi listo para mostrarte la propiedad ideal! "
                            f"Pero antes necesito un detalle más: {sugerencia}"
                        )

                        memory.add_message(session_id, "user", data.message)
                        memory.add_message(session_id, "assistant", respuesta)
                        memory.set_flag(session_id, "mostrar_propiedad", False)

                        return ChatResponse(response=respuesta)

        logger.debug("🔕 Faltan confirmaciones, consultando al modelo sin propiedad", extra={"session_id": session_id})
        if flags.get("filtros_completos") and not flags.get("mostrar_propiedad"):
            history.append({
                "role": "system",
                "content": (
                    "Aunque el usuario ha proporcionado suficientes datos para encontrar una propiedad, "
                    "NO debes inventar ninguna propiedad ni suponer resultados. Espera a que el usuario "
                    "confirme explícitamente que desea ver las propiedades. Puedes seguir conversando normalmente."
                )
            })

        model_response = await llm.chat(data.message, history)

        propiedades = db.query(Inmueble).filter(Inmueble.slug != None).all()
        nombres_propiedades = [p.titulo for p in propiedades]
        mencionadas = get_close_matches(model_response, nombres_propiedades, n=1, cutoff=0.6)

        if mencionadas:
            logger.debug("🔗 El modelo mencionó una propiedad real", extra={"session_id": session_id, "mencionada": mencionadas[0]})
            inmueble = next((p for p in propiedades if p.titulo == mencionadas[0]), None)
            if inmueble and inmueble.imagenes:
                imagenes = [img.url_imagen for img in inmueble.imagenes[:3] if img.url_imagen]
                if imagenes:
                    url = f"https://multihabitat.lat/inmueble/{inmueble.slug}/"
                    group_id = uuid4().hex
                    imagenes_html = "".join([
                        f'<img src="{img}" data-full="{img}" data-group="{group_id}" loading="lazy" class="zoomable-img" '
                        f'style="width: 120px; max-width: 100%; border-radius: 10px; '
                        f'margin-right: 0.5rem; margin-bottom: 0.5rem; cursor: zoom-in;" alt="{inmueble.titulo}">'
                        for img in imagenes
                    ])
                    model_response += (
                        f"<div style='display: flex; flex-wrap: wrap; margin-top: 0.25rem; margin-bottom: 0.5rem;'>"
                        f"{imagenes_html}</div>"
                        f"<a href='{url}' target='_blank' "
                        f"style='display: inline-flex; align-items: center; gap: 0.4rem; color: #0d6efd; "
                        f"text-decoration: none; font-weight: 500;'>"
                        f"<i class='bi bi-box-arrow-up-right'></i> Ver esta propiedad en Multihabitat</a>"
                    )

        memory.add_message(session_id, "user", data.message)
        memory.add_message(session_id, "assistant", model_response)
        logger.info("📤 Respuesta generada (sin mostrar propiedad)", extra={"session_id": session_id})
        model_response = limpiar_texto_parentesis(model_response)
        model_response = limpiar_prefijo_llm(model_response)
        return ChatResponse(response=model_response)

    except Exception as e:
        logger.error("💥 Error en el endpoint /chat", exc_info=True, extra={"session_id": session_id})
        raise HTTPException(status_code=500, detail="Error interno al procesar el mensaje.")