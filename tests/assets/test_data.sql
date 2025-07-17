-- Crear tabla inmueble
CREATE TABLE inmueble (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    slug TEXT UNIQUE,
    descripcion TEXT,
    descripcion_corta TEXT,
    tipo TEXT,
    precio REAL NOT NULL,
    ubicacion TEXT,
    barrio TEXT,
    ciudad TEXT,
    area_m2 REAL NOT NULL,
    habitaciones INTEGER NOT NULL,
    banos INTEGER NOT NULL,
    carros INTEGER NOT NULL,
    estado TEXT NOT NULL,
    fecha_publicacion DATETIME
);

-- Crear tabla imagenes_inmuebles
CREATE TABLE imagenes_inmuebles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_imagen TEXT,
    orden INTEGER,
    inmueble_id INTEGER,
    FOREIGN KEY (inmueble_id) REFERENCES inmueble(id)
);

-- Crear tabla mapa_inmuebles
CREATE TABLE mapa_inmuebles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    inmueble_id INTEGER,
    FOREIGN KEY (inmueble_id) REFERENCES inmueble(id)
);

-- Insertar inmueble
INSERT INTO inmueble (titulo, slug, precio, area_m2, habitaciones, banos, carros, estado, ciudad)
VALUES ('Casa en Chapinero', 'casa-en-chapinero', 350000000, 85, 3, 2, 1, 'disponible', 'Bogotá');

-- Insertar imagenes para inmueble 1
INSERT INTO imagenes_inmuebles (url_imagen, orden, inmueble_id)
VALUES ('http://ejemplo.com/img1.jpg', 1, 1),
        ('http://ejemplo.com/img2.jpg', 2, 1);

-- Insertar mapa para inmueble 1
INSERT INTO mapa_inmuebles (latitud, longitud, inmueble_id)
VALUES (4.6479, -74.0628, 1);
