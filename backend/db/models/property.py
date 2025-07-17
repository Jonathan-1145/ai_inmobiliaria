from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from backend.db.database import Base
from datetime import datetime, timezone

class Inmueble(Base):
    __tablename__ = "inmueble"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    slug = Column(String, nullable=True, unique=True)
    descripcion = Column(String, nullable=True)
    descripcion_corta = Column(String, nullable=True)
    tipo = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    ubicacion = Column(String, nullable=True)
    barrio = Column(String, nullable=True)
    ciudad = Column(String, nullable=True)
    area_m2 = Column(Float, nullable=False)
    habitaciones = Column(Integer, nullable=False)
    banos = Column(Integer, nullable=False)
    carros = Column(Integer, nullable=False)
    estado = Column(String, nullable=False)
    fecha_publicacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    imagenes = relationship("ImagenInmueble", back_populates="inmueble")
    mapa = relationship("MapaInmueble", uselist=False, back_populates="inmueble")

class MapaInmueble(Base):
    __tablename__ = "mapa_inmuebles"

    id = Column(Integer, primary_key=True)
    latitud = Column(DECIMAL(9, 6))
    longitud = Column(DECIMAL(9, 6))
    inmueble_id = Column(Integer, ForeignKey("inmueble.id"))
    inmueble = relationship("Inmueble", back_populates="mapa")
