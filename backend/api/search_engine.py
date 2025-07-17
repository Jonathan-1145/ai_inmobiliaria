from backend.db.models.property import Inmueble
from backend.logger_setup import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)

def buscar_propiedad_ideal(db: Session, filtros: dict) -> Inmueble | None:
    """
    Realiza una búsqueda optimizada basada en los filtros dados y devuelve 
    la propiedad que más coincidencias tenga.
    """
    propiedades = db.query(Inmueble).all()
    logger.debug("🔍 Iniciando búsqueda de propiedad ideal", extra={
        "filtros_recibidos": filtros,
        "cantidad_propiedades_en_bd": len(propiedades)
    })

    if not propiedades:
        logger.warning("⚠️ No hay propiedades en la base de datos")
        return None

    def contar_coincidencias(inmueble: Inmueble) -> int:
        score = 0
        if filtros.get("tipo") and inmueble.tipo and filtros["tipo"].lower() == inmueble.tipo.lower():
            score += 3
        if filtros.get("precio") and inmueble.precio and inmueble.precio <= filtros["precio"]:
            score += 2
        if filtros.get("barrio") and inmueble.barrio and filtros["barrio"].lower() in inmueble.barrio.lower():
            score += 4
        if filtros.get("ciudad") and inmueble.ciudad and filtros["ciudad"].lower() in inmueble.ciudad.lower():
            score += 3
        if filtros.get("area_m2") and inmueble.area_m2 and inmueble.area_m2 >= filtros["area_m2"]:
            score += 2
        if filtros.get("habitaciones") and inmueble.habitaciones and inmueble.habitaciones >= filtros["habitaciones"]:
            score += 2
        if filtros.get("banos") and inmueble.banos and inmueble.banos >= filtros["banos"]:
            score += 1
        if filtros.get("carros") and inmueble.carros and inmueble.carros >= filtros["carros"]:
            score += 1
        return score

    propiedades_ordenadas = sorted(propiedades, key=contar_coincidencias, reverse=True)
    mejor_propiedad = propiedades_ordenadas[0]
    score_mejor = contar_coincidencias(mejor_propiedad)

    logger.debug("🏡 Mejor propiedad seleccionada", extra={
        "titulo": mejor_propiedad.titulo if mejor_propiedad else "N/A",
        "score": score_mejor
    })

    if score_mejor > 0:
        return mejor_propiedad
    else:
        logger.info("ℹ️ Ninguna propiedad coincidió suficientemente con los filtros")
        return None
