from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.database import Base

class ImagenInmueble(Base):
    __tablename__ = "imagenes_inmuebles"

    id = Column(Integer, primary_key=True)
    url_imagen = Column(String(500), nullable=True)
    orden = Column(Integer)
    inmueble_id = Column(Integer, ForeignKey("inmueble.id"))
    inmueble = relationship("Inmueble", back_populates="imagenes")