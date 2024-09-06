import sqlite3
import os

# Conectar a la base de datos SQLite, especificando la ruta absoluta a la carpeta 'db'
db_path = os.path.join(os.path.dirname(__file__), 'gasotrack.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear las tablas si no existen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Estacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        horario TEXT,
        tipo TEXT CHECK (tipo IN ('Subsidiada', 'Internacional'))
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Combustible (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        octanaje INTEGER
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS EstacionCombustible (
        estacion_id INTEGER,
        combustible_id INTEGER,
        FOREIGN KEY (estacion_id) REFERENCES Estacion(id),
        FOREIGN KEY (combustible_id) REFERENCES Combustible(id),
        PRIMARY KEY (estacion_id, combustible_id)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reporte (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estacion_id INTEGER,
        combustible_id INTEGER,
        fechahora DATETIME DEFAULT CURRENT_TIMESTAMP,
        disponibilidad TEXT CHECK (disponibilidad IN ('Sí', 'No')),
        FOREIGN KEY (estacion_id) REFERENCES Estacion(id),
        FOREIGN KEY (combustible_id) REFERENCES Combustible(id)
    );
""")

# Poblar la tabla Combustible
combustibles = [
    ('Diesel', None),
    ('91 Octanos', 91),
    ('95 Octanos', 95)
]
cursor.executemany("INSERT INTO Combustible (nombre, octanaje) VALUES (?, ?)", combustibles)

conn.commit()
conn.close()

print("Tablas creadas y Combustible poblada correctamente.")