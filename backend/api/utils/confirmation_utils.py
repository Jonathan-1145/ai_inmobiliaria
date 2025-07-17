import re
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import logging
import torch

logger = logging.getLogger("confirmation")

# === Modelo de embeddings cargado una vez ===
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# === Confirmaciones base para comparación semántica ===
_frases_confirmacion = [
    # Confirmaciones Directas
    "muéstramela",
    "muéstrame",
    "dale",
    "claro",
    "sí",
    "por supuesto",
    "a ver",
    "quiero verla",
    "enséñamela",
    "ver la propiedad",
    "mostrar la casa",
    "quiero ver opciones",
    "ver resultados",
    "sí quiero verla",
    "claro que sí, muéstramela",
    "me gustaría verla",
    "podrías mostrármela",
    "déjamela ver",
    "la quiero ver",
    "sí, quiero verla"

    # Confirmaciones Informales y/o Conversacionales
    "dale, muéstramela",
    "de una, enséñamela",
    "a ver qué tenés",
    "muéstrame qué hay",
    "que no se diga más, muéstrala",
    "qué opciones tienes por ahí",
    "tírame el dato",
    "soltá lo que tengas",
    "mostrame lo que hay",
    "de una, mostrame esa casa",
    "ya pues, enséñamela",

    # Frases Estilo 'Eso me interesa'
    "esa me sirve",
    "me interesa esa opción",
    "me gustó esa",
    "suena buena, quiero verla",
    "esa podría funcionar",
    "esa está bien",
    "esa puede ser",
    "me llamó la atención esa",
    "esa pinta bien",
    "creo que esa me interesa",

    # Confirmaciones Cortas o Implícitas
    "verla",
    "ver eso",
    "ok, muéstrala",
    "hazlo",
    "muéstrame ya",
    "veámosla",
    "dale pues",
    "listo, quiero verla",
    "bueno, veamos esa",

    # Confirmaciones con Intención de Tomar Acción
    "quiero ver detalles",
    "muéstrame fotos",
    "ver más información",
    "quiero más datos",
    "quiero saber más",
    "muéstrame el link",
    "ver ubicación",
    "ver fotos y precio",

    # Estilo Cliente Formal
    "quisiera ver la propiedad",
    "me interesa conocer más detalles",
    "¿podría ver la propiedad?",
    "¿me la puedes mostrar?",
    "¿sería posible verla?",
    "quisiera más información sobre esa opción",
    "¿puede enviarme los detalles?",

    # Neutras Pero Confirmatorias
    "esa opción está bien",
    "podría funcionar",
    "quiero verla mejor",
    "quiero analizarla",
    "quiero revisar esa",
]

_vector_confirmaciones = _model.encode(_frases_confirmacion)

def es_confirmacion_por_regex(text: str) -> bool:
    text = text.lower()
    patrones_confirmacion = [
        # Afirmaciones simples y universales
        r"\b(s[ií]|sí quiero|claro que s[ií]|sí deseo|sí, por favor|vale|ok|dale|de una|claro|vamos|hazlo|listo|hecho|bueno)\b",
        
        # Verbos de ver y mostrar directamente
        r"\b(m[uú]estramela|ens[eé]ñamela|déjamela ver|quiero verla|quiero ver|ens[eé]ñame)\b",
        r"\b(m[ueé]strame|ens[eé]ñame|verla ya|verla ahora|verla pues|mostrar)\b",

        # Frases como "quiero ver una opción / alternativa / inmueble"
        r"\b(quiero|mu[ée]strame|ens[eé]ñame|ver)\b.*\b(algo|una|opci[oó]n|alternativa|inmueble|casa|apartamento|propiedad|oferta|lugar)\b",

        # Confirmaciones estilo colombiano
        r"\b(a ver qu[eé] ten[eé]s|mu[ée]strame qu[eé] hay|suelta lo que tengas|t[ií]rame el dato|mostrame lo que hay)\b",
        r"\b(de una mu[ée]stramela|ya pues ens[eé]ñamela|dale pues|ya quiero verla|mostr[aá]mela ya)\b",

        # Decisiones implícitas
        r"\b(est[aá] bien|perfecto|eso quiero|esa me interesa|me interesa|acepto|quiero esa|me sirve|me gust[oó])\b",

        # Peticiones comunes en Colombia
        r"\b(ver detalles|ver fotos|ver m[aá]s|ver info|ver informaci[oó]n|ver precio|ver ubicaci[oó]n)\b",

        # Cierre con intención
        r"\b(listo, veamos|bueno, mu[ée]strala|dale, quiero verla|ya pues, mu[ée]strala)\b",
    ]
    return any(re.search(p, text) for p in patrones_confirmacion)

def es_confirmacion_usuario_embeddings(message: str) -> bool:
    vector_usuario = _model.encode([message])
    similitudes = cosine_similarity(vector_usuario, _vector_confirmaciones)[0]
    logger.debug("Similitud por embeddings:", extra={"input": message, "scores": similitudes.tolist()})
    return any(score >= 0.75 for score in similitudes)

def es_confirmacion_usuario(message: str) -> bool:
    return es_confirmacion_por_regex(message) or es_confirmacion_usuario_embeddings(message)

# Frases que representan indiferencia
frases_indiferencia = [
    # Comúnes
    "no me importa", 
    "me da igual", 
    "cualquiera está bien", 
    "lo que tengas", 
    "no tengo preferencia",
    "puede ser cualquiera", 
    "no importa cuál", 
    "estoy abierto a opciones", 
    "sorpréndeme", 
    "lo que sea",
    "el que sea", 
    "como sea", 
    "me sirve cualquiera", 
    "la que tengas", 
    "lo que me muestres",
    "da lo mismo", 
    "no soy exigente",

    # Expresiones Reales Usadas en Colombia
    "el que salga está bien",
    "lo que salga",
    "como caiga",
    "eso no importa mucho",
    "no me fijo en eso",
    "con lo que haya está bien",
    "no tengo lío con eso",
    "lo que se pueda",
    "no tengo problema",
    "lo que aparezca",
    "no tengo rollo con eso",
    "con lo que consigas me sirve",
    "eso no es tan relevante para mí",
    "eso no es prioridad",
    "no tengo una idea clara de eso",
    "lo que haya disponible",
    "me acomodo a lo que haya",
    "escoja por mí",
    "usted diga",
    "usted verá",
    "me dejo guiar",
    "lo que usted vea",
    "escoja la que crea mejor",
    "confío en lo que me muestres",
    "todo bien con cualquiera",
    "no soy tan exigente en eso",
    "no importa mucho ese detalle",
    "déjalo al azar jaja",
    "no tengo una preferencia fija",
    "lo que te parezca bien",
    "me acomodo fácil",
    "con que sea decente, me sirve",
]

# Precalcular los embeddings de esas frases
embeddings_indiferencia = _model.encode(frases_indiferencia, convert_to_tensor=True)

def es_indiferencia_usuario_embeddings(mensaje: str, umbral: float = 0.75) -> bool:
    """
    Detecta si el usuario expresa indiferencia usando similitud semántica con embeddings.
    """
    try:
        emb_mensaje = _model.encode([mensaje], convert_to_tensor=True)
        similitudes = util.pytorch_cos_sim(emb_mensaje, embeddings_indiferencia)[0]
        max_score = torch.max(similitudes).item()

        return max_score >= umbral
    except Exception as e:
        # Por si hay algún error en ejecución
        print(f"[⚠️ Error en es_indiferencia_usuario_embeddings]: {e}")
        return False
    
# Frases que la IA Usará Cuando le Falten Filtros
SUGERENCIAS_FILTROS_FALTANTES = {
    "tipo": "que me digas qué tipo de propiedad prefieres: una casa, un apartamento, un local comercial… lo que tengas en mente",

    "ciudad": "saber en qué ciudad estás buscando, así enfoco mejor las opciones para ti",

    "barrio": "conocer si tienes algún barrio o zona preferida para priorizar lo que más te gusta",

    "habitaciones": "una idea del número de habitaciones que necesitas, según cuántas personas vivirán allí o cómo usarías el espacio",

    "banos": "cuántos baños consideras cómodos, sobre todo si es para familia o si quieres un baño privado",

    "area_m2": "una aproximación del área en metros cuadrados, así sea algo general como “grande” o “compacto”",
}
