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

_vector_confirmaciones = _model.encode(_frases_confirmacion)

def es_confirmacion_por_regex(text: str) -> bool:
    text = text.lower()
    patrones_confirmacion = [

        # === Afirmaciones generales / simples ===
        r"\b(s[ií]|sí quiero|sí deseo|sí por favor|claro que s[ií]|claro|vale|ok|okay|bueno|hecho|dale|de una|vamos|hazlo|listo|simon|affirmative|as[ií] es|obvio|seguro|confirm[oó]|por supuesto)\b",

        # === Verbos de mostrar / ver directamente ===
        r"\b(m[uú]estramela|ens[eé]ñamela|déjamela ver|quiero verla|quiero ver|mu[ée]strame|ens[eé]ñame|verla ya|verla ahora|verla pues|mostrar|mostrarla|ver opciones|ver resultados|mostrar resultados|ver propiedad|ver la casa)\b",

        # === Peticiones directas + objetos relacionados ===
        r"\b(quiero|mu[ée]strame|ens[eé]ñame|ver|ens[eé]name)\b.*\b(algo|una|opci[oó]n|alternativa|inmueble|casa|apartamento|propiedad|oferta|lugar|sitio|vivienda)\b",

        # === Confirmaciones estilo informal / colombiano / latino ===
        r"\b(a ver qu[eé] ten[eé]s|mu[ée]strame qu[eé] hay|suelta lo que tengas|t[ií]rame el dato|solt[aá] lo que tengas|mostrame lo que hay|de una|de una parcero|ya pues|ya quiero verla|mostr[aá]mela ya|ya mismo|ya mu[ée]strala|ahora mu[ée]stramela)\b",

        # === Expresiones de aceptación o elección implícita ===
        r"\b(est[aá] bien|perfecto|eso quiero|esa quiero|esa me interesa|me interesa|acepto|me sirve|quiero esa|me gust[oó]|esa est[aá] bien|esa me gusta|me gust[oó] esa|me llama la atenci[oó]n|esa puede ser|esa me convence|me voy con esa)\b",

        # === Peticiones con intención de ver más información ===
        r"\b(ver detalles|ver fotos|ver m[aá]s|ver info|ver informaci[oó]n|ver precio|ver ubicaci[oó]n|mostrar fotos|mostrar m[aá]s datos|mu[ée]strame el link|ver link|ver mapa|ver todo|ver ficha)\b",

        # === Confirmaciones indirectas o de cierre ===
        r"\b(listo, veamos|bueno, mu[ée]strala|dale, quiero verla|ya pues, mu[ée]strala|veamos esa|hazlo ya|mu[ée]strala entonces|mu[ée]strame entonces|dale con esa|mu[ée]strame esa|quiero ver esa|esa es|esa quiero|mu[ée]strame la opci[oó]n)\b",

        # === Expresiones con modismos o frases de calle ===
        r"\b(lanzate con esa|tira esa ya|dale con la que tengas|muestra lo que hay|t[íi]rate una|muestrame lo que tengas|dale, de una|mu[ée]strame lo que ten[eé]s|mu[ée]strame pues|ya estoy listo|m[ueé]strame nom[aá]s|veamos esa vaina)\b",

        # === Preguntas con intención de ver ===
        r"\b(puedo verla\??|me la puedes mostrar\??|la puedo ver\??|me muestras esa\??|me enseñas esa\??|me enseñas la casa\??|puedo ver opciones\??|me puedes mostrar\??|me enseñas algo\??|hay algo para ver\??)\b",

        # === Afirmaciones con intención de acción inmediata ===
        r"\b(ya quiero ver|quiero eso|mu[ée]strame ya|vamos a eso|hazlo ya|mostr[aá] ya|dale sin miedo|mu[ée]strame sin pensarlo)\b",
    ]
    return any(re.search(p, text) for p in patrones_confirmacion)


def es_confirmacion_usuario_embeddings(message: str) -> bool:
    vector_usuario = _model.encode([message])
    similitudes = cosine_similarity(vector_usuario, _vector_confirmaciones)[0]
    logger.debug("Similitud por embeddings:", extra={"input": message, "scores": similitudes.tolist()})
    return any(score >= 0.65 for score in similitudes)

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

    # Nuevas expresiones comunes/neutras
    "lo que tú digas",
    "elige tú",
    "cualquiera me funciona",
    "la que tú creas mejor",
    "yo no escojo, tú decide",
    "la que te parezca bien",
    "dale a cualquiera",
    "escoge tú",
    "no tengo inclinación",
    "todas me parecen bien",
    "como tú veas",
    "no me decido, elige por mí",
    "que sea lo que Dios quiera",
    "todas suenan bien",
    "ninguna en especial",
    "la que quieras mostrar",
    "como tú prefieras",
    "tú mandas",
    "a tu criterio",
    "a mí me da lo mismo",

    # Informales o con humor
    "lánzate con la que sea",
    "saca una al azar",
    "el destino dirá",
    "lo que caiga primero",
    "escoge con los ojos cerrados",
    "me lanzo a lo que sea",
    "esa vaina me da igual",
    "yo le jalo a todo",
    "esa vuelta no me afecta",
    "eso no me quita el sueño",
    "yo me dejo llevar",
    "lo que quieras mostrar primero",
    "échale suerte",
    "tú verás qué me das",
    "tírate una cualquiera",
    "el azar manda",

    # Estilo colaborativo/sumiso (cliente relajado)
    "confío en tu criterio",
    "muéstrame lo que tú creas",
    "yo te sigo",
    "lo que tú escojas está bien",
    "me adapto",
    "a mí todo me parece",
    "lo que tú veas conveniente",
    "muéstrame cualquier opción",
    "tú decides por mí",
    "la que tú prefieras",

    # Estilo resignado/despreocupado
    "igual me va a tocar",
    "todo me da lo mismo",
    "ni idea, lo que sea",
    "no sé, escoge tú",
    "yo ni opino, muéstrame nomás",
]

# Precalcular los embeddings de esas frases
embeddings_indiferencia = _model.encode(frases_indiferencia, convert_to_tensor=True)

def es_indiferencia_usuario_embeddings(mensaje: str, umbral: float = 0.65) -> bool:
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
