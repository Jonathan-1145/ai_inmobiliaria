from sqlalchemy.orm import sessionmaker, declarative_base
from backend.logger_setup import get_logger
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

logger = get_logger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    logger.info("🔌 Motor de base de datos creado correctamente")
except Exception as e:
    logger.error(f"❌ Error al crear motor de BD: {e}", exc_info=True)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    logger.debug("🗄️ Nueva sesión de base de datos iniciada")
    try:
        yield db
    finally:
        db.close()
        logger.debug("🗄️ Sesión de base de datos cerrada")
