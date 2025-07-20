from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from backend.db.models.property import Inmueble
from backend.logger_setup import get_logger
from difflib import get_close_matches
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session
import string
import re

from backend.api.utils.dictionaries import (
    BARRIOS, URBANIZACIONES, PARCELACIONES_CAMPESTRES,
    CORREGIMIENTOS_VEREDAS
)
from backend.api.utils.ubicaciones_guadalajara_de_buga import UBICACIONES_GUADALAJARA_DE_BUGA

logger = get_logger(__name__)

# === Carga de modelo de palabras para detectar los filtros ===
REGEX_BASE = {
    "tipo": {
        "Finca": r"\b(finca(s)?|granja|hacienda|parcel[a|as]|quinta)\b",
        "Casa": r"\b(casa(s)?|vivienda(s)?|hogar(es)?)\b",
        "Apartamento": r"\b(apartamento(s)?|apto(s)?|departamento(s)?|depto(s)?)\b",
        "Apartaestudio": r"\b(apartaestudio(s)?|estudio(s)?|loft(s)?|monoambiente(s)?)\b",
        "Lote": r"\b(lote(s)?|terreno(s)?|solar(es)?|parcel[a|as])\b",
        "Local Comercial": r"\b(local(es)?( comercial(es)?)?|negocio(s)?|tienda(s)?|almac[eé]n(es)?)\b"
    },

    "habitaciones": r"(\d{1,2})\s*(habitaci[oó]n|habitaciones|cuarto|cuartos|alcoba|alcobas)",
    "banos": r"(\d{1,2})\s*(bañ[oa]s?|bañitos|baños|sanitarios|servicios higi[eé]nicos?)",
    "carros": r"(\d{1,2})\s*(garaje|parqueadero|veh[ií]culo|carro|carros|auto|autos)",
    "area_m2": r"(\d{2,4})\s*(m2|mts|metros\s+cuadrados?)",
    "precio": r"(\$?\d+(?:[\.,]?\d+)?)(?:\s?(mil|millones|mill[oó]n|k|k\s?cop|cop|m)?)"
}

# === Carga de modelo ligero para embeddings semánticos ===
modelo_embed = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
frases_confirmacion = [
    # Confirmaciones Directas
    "muéstrame la propiedad",
    "quiero verla",
    "enséñamela",
    "ver más detalles",
    "muéstramela",
    "quiero ver opciones",
    "ver resultados",
    "sí quiero verla",
    "mostrar propiedad",
    "ver detalles de la casa",
    "déjamela ver",

    # Frases Cortas e Informales
    "verla",
    "ver eso",
    "ver la opción",
    "ver alternativa",
    "ok, muéstramela",
    "dale, quiero verla",
    "a ver qué tienes",
    "hazlo",
    "listo, quiero verla",
    "de una, muéstrame",
    "ya quiero verla",

    # Estilo Cliente Relajado
    "mostrame lo que hay",
    "tírame el dato",
    "suelta lo que tengas",
    "a ver qué hay",
    "muéstrame qué hay por ahí",
    "a ver si esa sirve",
    "mostrámela",
    "déjala ver",
    "eso me interesa, muéstrala",
    "quiero ver esa casa",
    "veamos esa",

    # Confirmaciones Implícitas
    "esa me interesa",
    "me interesa verla",
    "me sirve esa",
    "esa podría funcionar",
    "suena bien esa",
    "creo que esa me gusta",
    "quiero saber más",
    "quisiera más información",
    "me gustaría verla",

    # Estilo Formal y Educado
    "podrías mostrármela",
    "¿me la puedes mostrar?",
    "es posible verla",
    "quisiera ver la propiedad",
    "me gustaría conocerla",
    "me gustaría verla",
    "me interesa conocer más detalles",

    # Regionalismos y Modismos Locales
    "de una, enséñamela",
    "ya pues, muéstramela",
    "eso está bien, muéstrala",
    "dale, mostrame esa",
    "déjamela ver un momentico",
    "veámosla entonces",

    # Estilo "Eso es todo"
    "eso es todo",
    "con eso está bien",
    "suficiente por ahora",
    "listo, gracias",
    "no necesito más",
    "hasta ahí está bien",
    "con eso me sirve",
    "ya con eso",
    "eso era",
    "no es más",

    # Estilo "Así está bien"
    "está perfecto así",
    "así está bien",
    "tal como está",
    "me parece bien",
    "me quedo con esa",
    "esa me gusta, gracias",
    "con esa opción me quedo",
    "esa está buena",
    "esa me convence",
    "funciona para mí",

    # Estilo "No necesito más info"
    "no hace falta más",
    "no me muestres más",
    "no tengo más preguntas",
    "ya me mostraste suficiente",
    "ya entendí",
    "ya vi lo que quería",
    "gracias, ya está",
    "cerramos con esa",
    "no busques más",
    "suficiente info por ahora",

    # Estilo informal / WhatsApp
    "joya",
    "va que va",
    "re bien, gracias",
    "todo bien",
    "finito",
    "eso era lo que quería",
    "ya estuvo",
    "de una, esa es",
    "cerramos",
    "va esa",
]
embeddings_base = modelo_embed.encode(frases_confirmacion, convert_to_tensor=True)

# === Cargar modelo de embeddings para usarlo ===
def get_embed_model():
    return modelo_embed

# === Ajustar el precio ===
def parse_precio(precio_str: str) -> int | None:
    """
    Convierte expresiones de precio como '500M', '2.5 millones', '100k COP', etc. a un entero en pesos colombianos (COP).
    Soporta errores comunes de escritura como 'millnes', 'milonez', etc.
    """
    texto = precio_str.lower().replace("$", "").strip()

    # Regex flexible para capturar número y unidad
    match = re.search(r"(\d+(?:[\.,]?\d+)?)(?:\s*([a-zA-Záéíóúñ]+))?", texto)
    if not match:
        logger.warning("No se pudo extraer valor del precio", extra={"input": precio_str})
        return None

    numero_str, unidad_raw = match.groups()
    unidad_raw = unidad_raw or ""
    
    try:
        numero = float(numero_str.replace(",", "."))
    except ValueError:
        logger.warning("Valor inválido al convertir precio", extra={"input": precio_str})
        return None

    # Lista base de unidades esperadas
    unidades_validas = {
        "millones": 1_000_000,
        "millón": 1_000_000,
        "millon": 1_000_000,
        "m": 1_000_000,
        "mil": 1_000,
        "k": 1_000,
        "kcop": 1_000,
        "cop": 1
    }

    unidad = None
    posibles = []
    
    if unidad_raw:
        unidad_raw = unidad_raw.strip()
        posibles = get_close_matches(unidad_raw, unidades_validas.keys(), n=1, cutoff=0.75)
        if posibles:
            unidad = posibles[0]
        else:
            logger.warning("Unidad desconocida en precio", extra={"unidad_detectada": unidad_raw})

    if posibles:
        unidad = posibles[0]
    else:
        unidad = corregir_unidad_con_embeddings(unidad_raw, modelo_embed)
        if not unidad:
            logger.warning("Unidad desconocida, incluso con embeddings", extra={"unidad_detectada": unidad_raw})
    
    if unidad:
        multiplicador = unidades_validas[unidad]
        return int(numero * multiplicador)
    else:
        # Si no hay unidad o es irreconocible, usar heurística:
        # Si el número es grande, se asume COP
        if numero > 10_000:
            return int(numero)
        else:
            return int(numero * 1_000_000)
        
PALABRAS_CLAVE_PRECIO = [
    "precio",
    "cueste",
    "vale",
    "coste",
    "costar", 
    "valor", 
    "pesos", 
    "millones", 
    "mil", 
    "$", 
    "mensual", 
    "mensuales", 
    "por mes", 
    "alquiler", 
    "venta", 
    "arriendo",
    "cuánto es",
    "cuánto cuesta",
    "cuánto vale",
    "cuánto sale",
    "cuánto cobran",
    "qué precio tiene",
    "qué valor tiene",
    "en cuánto está",
    "qué cuesta",
    "está caro",
    "es barato",
    "tarifa",
    "costo",
    "importe",
    "pago mensual",
    "canon",
    "honorarios",
    "plata",
    "cuánto billete",
    "cuánto cash",
    "cuánto hay que pagar",
    "cuánto toca",
    "en cuánto me lo dejas",
    "cuánto me sale",
    "cuánta guita",
    "cuánto varo",
    "cuánto baro",
    "financiación",
    "cuotas",
    "interés",
    "abono",
    "enganche",
    "anticipo",
    "subsidio",
    "usd",
    "us$",
    "dólares",
    "dolar",
    "euros",
    "€"
]

def es_contexto_de_precio(texto):
    texto_emb = modelo_embed.encode(texto, convert_to_tensor=True)
    ejemplos = PALABRAS_CLAVE_PRECIO
    ejemplos_emb = modelo_embed.encode(ejemplos, convert_to_tensor=True)

    similitudes = util.cos_sim(texto_emb, ejemplos_emb)
    return similitudes.max() > 0.65

def contiene_palabra_similar(texto: str, palabras_clave: list, umbral=80) -> bool:
    """
    Devuelve True si al menos una palabra del texto se parece a alguna palabra clave.
    """
    palabras_texto = texto.lower().split()
    for palabra in palabras_texto:
        for clave in palabras_clave:
            if fuzz.ratio(palabra, clave) >= umbral:
                return True
    return False

def corregir_unidad_con_embeddings(unidad_raw: str, modelo) -> str | None:
    unidades_validas = ["mil", "millón", "millones", "m", "k", "cop"]
    unidad_emb = modelo.encode([unidad_raw], convert_to_tensor=True)
    unidades_emb = modelo.encode(unidades_validas, convert_to_tensor=True)
    similitudes = util.cos_sim(unidad_emb, unidades_emb)[0]
    idx_max = similitudes.argmax().item()
    if similitudes[idx_max] > 0.6:
        return unidades_validas[idx_max]
    return None

def elegir_precio_mas_confiable(matches):
    mejores = []

    for match in matches:
        grupos = [g for g in match if g]
        expresion = " ".join(grupos).lower()
        valor = parse_precio(expresion)
        if valor is None:
            continue

        tiene_unidad = contiene_palabra_similar(expresion, ["mil", "millón", "millones", "$", "pesos", "k", "m"])
        contexto_precio = contiene_palabra_similar(expresion, ["cueste", "vale", "precio", "arriendo", "alquiler", "venta", "mensuales", "mensual", "por", "mes", "mensualmente"])

        puntuacion = 0
        if tiene_unidad:
            puntuacion += 2
        if contexto_precio:
            puntuacion += 1

        mejores.append((valor, puntuacion))

    if mejores:
        mejores.sort(key=lambda x: x[1], reverse=True)
        mejor_valor, mejor_puntuacion = mejores[0]
        if mejor_puntuacion >= 1:
            return mejor_valor

    return None

# === Extraer los filtros a partir del texto ===
def extract_filters_from_text(message: str, db: Session, current_filters: dict) -> dict:
    text = message.lower()
    filters = current_filters.copy()
    text_tokens = text.translate(str.maketrans("", "", string.punctuation)).split()
    # --- Procesar cada campo con expresiones regulares ---
    for field, pattern_or_dict in REGEX_BASE.items():
        if field == "precio":
            matches = re.findall(pattern_or_dict, text)
            mejor_precio = elegir_precio_mas_confiable(matches)
            if mejor_precio:
                filters[field] = mejor_precio
            continue

        if isinstance(pattern_or_dict, dict):
            for value, pattern in pattern_or_dict.items():
                if value not in filters and re.search(pattern, text):
                    filters[field] = value
        else:
            matches = re.findall(pattern_or_dict, text)
            if matches:
                try:
                    numeros = [int(m[0]) for m in matches if m[0].isdigit()]
                    if numeros:
                        filters[field] = max(numeros)
                except Exception as e:
                    logger.warning("Error al interpretar valores numéricos", extra={"error": str(e), "matches": matches})

    # Unificar todas las ubicaciones de Buga
    ubicaciones_buga = set()

    for comuna_dict in [BARRIOS, URBANIZACIONES]:
        for barrios in comuna_dict.values():
            ubicaciones_buga.update(barrios)

    for zonas_dict in [CORREGIMIENTOS_VEREDAS, PARCELACIONES_CAMPESTRES]:
        for subzona in zonas_dict.values():
            if isinstance(subzona, dict):
                for veredas in subzona.values():
                    ubicaciones_buga.update(veredas)
            else:
                ubicaciones_buga.update(subzona)

    # Agregar explícitamente las del mapa de ubicaciones
    ubicaciones_buga.update(UBICACIONES_GUADALAJARA_DE_BUGA.keys())

    ubicaciones_lower = {u.lower(): u for u in ubicaciones_buga}
    n = len(text_tokens)
    frases_generadas = []

    # Sliding windows de 1 a 5 tokens
    for size in range(1, 6):
        for i in range(n - size + 1):
            frase = " ".join(text_tokens[i:i + size])
            frases_generadas.append(frase)

    for fragmento in frases_generadas:
        posibles = get_close_matches(fragmento, list(ubicaciones_lower.keys()), n=1, cutoff=0.8)
        if posibles:
            ubicacion_detectada = ubicaciones_lower[posibles[0]]
            if not filters.get("barrio"):
                filters["barrio"] = ubicacion_detectada
            if not filters.get("ciudad") and ubicacion_detectada in UBICACIONES_GUADALAJARA_DE_BUGA:
                filters["ciudad"] = UBICACIONES_GUADALAJARA_DE_BUGA[ubicacion_detectada]
            logger.debug("Ubicación detectada por fuzzy sliding window", extra={
                "input_fragment": fragmento,
                "match": ubicacion_detectada
            })
            break

    # --- Extraer ciudad y barrio desde la BD con más precisión ---
    ciudades = {i.ciudad.strip() for i in db.query(Inmueble.ciudad).distinct() if i.ciudad}
    barrios = {i.barrio.strip() for i in db.query(Inmueble.barrio).distinct() if i.barrio}

    for ciudad in ciudades:
        if ciudad.lower() in text and "ciudad" not in filters:
            filters["ciudad"] = ciudad

    for barrio in barrios:
        if barrio.lower() in text and "barrio" not in filters:
            filters["barrio"] = barrio

    # Si no se detectó 'tipo', intentar con embeddings
    if "tipo" not in filters:
        tipos_validos = list(REGEX_BASE["tipo"].keys())
        embedding_mensaje = modelo_embed.encode([text], convert_to_tensor=True)
        embedding_tipos = modelo_embed.encode(tipos_validos, convert_to_tensor=True)
        similitudes = util.pytorch_cos_sim(embedding_mensaje, embedding_tipos)[0]

        idx_max = similitudes.argmax().item()
        score_max = similitudes[idx_max].item()

        if score_max >= 0.7:
            filters["tipo"] = tipos_validos[idx_max]
            logger.debug("Tipo detectado por embeddings", extra={
                "mensaje": message,
                "tipo_detectado": tipos_validos[idx_max],
                "similitud": round(score_max, 4)
            })

    if filters == current_filters:
        logger.warning("⚠️ No se detectaron nuevos filtros en el mensaje", extra={"mensaje": message})

    logger.debug("Filtros extraídos desde el texto", extra={"mensaje": message, "resultado": filters})

    return filters

# === Definir que los filtros están completos para devolver True ===
VALORES_INDEFINIDOS = {None, "", -1, "indiferente", "no importa"}

def filters_estan_completos(filtros: dict) -> bool:
    campos_requeridos = ["tipo", "ciudad", "barrio", "habitaciones", "banos", "area_m2"]
    resultado = all(filtros.get(k) not in VALORES_INDEFINIDOS for k in campos_requeridos)
    logger.debug("Verificación de filtros completos", extra={"filtros": filtros, "resultado": resultado})
    return resultado

# === Limpiar las propiedades inventadas por la IA ===
def limpiar_si_invento_propiedad(texto: str, db: Session) -> str:
    """
    Si el texto menciona propiedades que no existen en base de datos, las elimina del texto.
    """
    propiedades = db.query(Inmueble).all()
    titulos_reales = [p.titulo.lower() for p in propiedades if p.titulo]

    # Buscar frases como "Te presento", "Aquí tienes", "Te recomiendo", etc.
    patrones = [
        r"(te (presento|muestro|recomiendo|sugiero)[^.:!]*(:|\.)?)",
        r"(una opción podría ser[^.:!]*(:|\.)?)",
        r"(esta propiedad llamada[^.:!]*(:|\.)?)"
    ]

    texto_original = texto

    for patron in patrones:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE)

    # Detectar títulos falsos usando similitud textual
    for linea in texto.splitlines():
        if any(titulo in linea.lower() for titulo in titulos_reales):
            continue
        if "casa" in linea.lower() and "#" in linea:
            texto = texto.replace(linea, "")

    # Limpieza final de espacios
    logger.debug("Texto limpiado de propiedades falsas", extra={"original": texto_original, "limpio": texto})
    return texto.strip()
