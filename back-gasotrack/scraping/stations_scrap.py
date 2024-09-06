import requests
import json
import sqlite3
import os

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

# Conectar a la base de datos SQLite, especificando la ruta absoluta a la carpeta 'db'
db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'gasotrack.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

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


