from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import tempfile
import sqlite3
import pytest
import os

@pytest.fixture
def temp_db():
    # Crear archivo .db temporal
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)  # Se cierra descriptor porque SQLAlchemy lo manejará

    # Cargar estructura y datos desde el .sql
    with sqlite3.connect(db_path) as conn:
        with open("tests/assets/test_data.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    # Crear motor y sesión SQLAlchemy
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # Se entrega al test

    # Cleanup: cerrar sesión y eliminar archivo .db
    session.close()
    os.remove(db_path)
