from backend.db.models.image import ImagenInmueble
from backend.db.models.property import Inmueble
from backend.db.schemas.property import InmuebleOut
from sqlalchemy.orm import Session, joinedload
from backend.logger_setup import get_logger
from sqlalchemy import and_, func

logger = get_logger(__name__)

def clean_str(value: str) -> str:
    return value.strip().lower() if isinstance(value, str) else value

def search_properties(
    db: Session,
    ciudad: str = None,
    barrio: str = None,
    tipo: str = None,
    precio_max: float = None,
    habitaciones: int = None,
    limit: int = 10,
    offset: int = 0,
):
    logger.info("🔎 Ejecutando búsqueda de propiedades", extra={
        "ciudad": ciudad,
        "barrio": barrio,
        "tipo": tipo,
        "precio_max": precio_max,
        "habitaciones": habitaciones,
        "limit": limit
    })

    ciudad = clean_str(ciudad)
    barrio = clean_str(barrio)
    tipo = clean_str(tipo)

    query = db.query(Inmueble).options(joinedload(Inmueble.imagenes))
    filters = []

    if ciudad:
        filters.append(func.lower(Inmueble.ciudad).ilike(f"%{ciudad}%"))
    if barrio:
        filters.append(func.lower(Inmueble.barrio).ilike(f"%{barrio}%"))
    if tipo:
        filters.append(func.lower(Inmueble.tipo).ilike(f"%{tipo}%"))
    if precio_max is not None:
        filters.append(Inmueble.precio <= precio_max)
    if habitaciones is not None:
        filters.append(Inmueble.habitaciones >= habitaciones)

    # Filtros adicionales de consistencia
    filters.append(Inmueble.ubicacion.isnot(None))
    filters.append(Inmueble.ciudad.isnot(None))
    filters.append(Inmueble.barrio.isnot(None))
    filters.append(Inmueble.estado.ilike("disponible"))

    query = query.filter(and_(*filters)).order_by(Inmueble.fecha_publicacion.desc())

    inmuebles = query.offset(offset).limit(limit).all()
    logger.info(f"✅ {len(inmuebles)} propiedades encontradas tras aplicar filtros")

    resultados = []

    for inmueble in inmuebles:
        imagenes_urls = [
            img.url_imagen for img in sorted(inmueble.imagenes, key=lambda x: x.orden)
            if img.url_imagen
        ][:3]

        if not imagenes_urls:
            logger.warning(f"⚠️ Propiedad '{inmueble.titulo}' sin imágenes válidas, se omitirá")
            continue

        url_detalle = f"https://multihabitat.lat/inmueble/{inmueble.slug}" if inmueble.slug else None

        inmueble_out = InmuebleOut.from_orm(inmueble).copy(update={
            "imagenes": imagenes_urls,
            "url_detalle": url_detalle
        })

        resultados.append(inmueble_out)

    logger.debug(f"Resultados procesados y listos para retornar. Total: {len(resultados)}")
    return resultados
