from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class InmuebleOut(BaseModel):
    id: int
    titulo: str
    slug: str
    descripcion: Optional[str]
    descripcion_corta: Optional[str]
    tipo: Optional[str]
    precio: float
    ubicacion: Optional[str]
    barrio: Optional[str]
    ciudad: Optional[str]
    area_m2: float
    habitaciones: int
    banos: int
    carros: int
    estado: str
    fecha_publicacion: datetime
    imagenes: List[str]
    url_detalle: str

    class Config:
        from_attributes = True