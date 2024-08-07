import requests
import json
import sqlite3

def obtener_estaciones_desde_osm(query):
    """Obtiene datos de estaciones de servicio desde OpenStreetMap usando Overpass API."""
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="fuel"](around:50000,10.5,-66.9); 
        );
        out body;
        >;
        out skel qt;
    """

    try:
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()

        estaciones = []
        for element in data['elements']:
            if element['type'] == 'node':
                estacion = {
                    'nombre': element['tags'].get('name', 'Nombre no disponible'),
                    'direccion': element['tags'].get('addr:street', 'Dirección no disponible') + ', ' + element['tags'].get('addr:city', 'Caracas'),
                    'latitud': element['lat'],
                    'longitud': element['lon']
                }
                estaciones.append(estacion)

        return estaciones

    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar a la API de Overpass. Verifica tu conexión a Internet.")
        return []  # Retornar una lista vacía si hay un error de conexión

# Conectar a la base de datos SQLite
conn = sqlite3.connect('gasotrack.db')
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

# Obtener estaciones desde OpenStreetMap
estaciones = obtener_estaciones_desde_osm(query="amenity=fuel")

if not estaciones:
    print("No se encontraron estaciones de servicio.")
else:
    # Insertar estaciones en la base de datos, asignando un valor predeterminado al tipo
    for estacion in estaciones:
        if 'tipo' not in estacion or estacion['tipo'] == 'Desconocido':
            estacion['tipo'] = 'Subsidiada'  # Asignar un valor predeterminado

        cursor.execute("""
            INSERT INTO Estacion (nombre, latitud, longitud, horario, tipo)
            VALUES (?, ?, ?, NULL, ?)
        """, (estacion['nombre'], estacion['latitud'], estacion['longitud'], estacion['tipo']))

        # Obtener el ID de la estación recién insertada
        estacion_id = cursor.lastrowid

        # Insertar combustibles para la estación (asumiendo que todas tienen los 3 tipos)
        for combustible_id in [1, 2, 3]: 
            cursor.execute("""
                INSERT INTO EstacionCombustible (estacion_id, combustible_id)
                VALUES (?, ?)
            """, (estacion_id, combustible_id))

    conn.commit()
    conn.close()

    print(estaciones)
