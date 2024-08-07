CREATE TABLE Estacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    latitud REAL NOT NULL,
    longitud REAL NOT NULL,
    horario TEXT,
    tipo TEXT CHECK (tipo IN ('Subsidiada', 'Internacional'))
);


CREATE TABLE Combustible (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    octanaje INTEGER
);

CREATE TABLE EstacionCombustible (
    estacion_id INTEGER,
    combustible_id INTEGER,
    FOREIGN KEY (estacion_id) REFERENCES Estacion(id),
    FOREIGN KEY (combustible_id) REFERENCES Combustible(id),
    PRIMARY KEY (estacion_id, combustible_id)
);

CREATE TABLE Reporte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estacion_id INTEGER,
    combustible_id INTEGER,
    fechahora DATETIME DEFAULT CURRENT_TIMESTAMP,
    disponibilidad TEXT CHECK (disponibilidad IN ('Sí', 'No')),
    FOREIGN KEY (estacion_id) REFERENCES Estacion(id),
    FOREIGN KEY (combustible_id) REFERENCES Combustible(id)
);
