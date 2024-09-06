from flask import Flask, jsonify, request, g
from datetime import datetime, timedelta
import sqlite3
import os
from models import *

app = Flask(__name__)

# Ruta absoluta a la base de datos en la carpeta 'db'
db_path = os.path.join(os.path.dirname(__file__), 'db', 'gasotrack.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(db_path)  
        g.db.row_factory = sqlite3.Row 

    return g.db


@app.route('/estaciones-get', methods=['GET'])
def obtener_estaciones():
    """
    Obtiene todas las estaciones de servicio de la base de datos y las devuelve en formato JSON.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Estacion")
    estaciones = cursor.fetchall()

    # Convertir los objetos Estacion a diccionarios para serializarlos en JSON
    lista_estaciones = []
    for estacion in estaciones:
        lista_estaciones.append({
            'id': estacion['id'],
            'nombre': estacion['nombre'],
            'latitud': estacion['latitud'],
            'longitud': estacion['longitud'],
            'horario': estacion['horario'],
            'tipo': estacion['tipo']
        })

    return jsonify(lista_estaciones)  


# Endpoint para obtener una estación por ID
@app.route('/estaciones/<int:estacion_id>', methods=['GET'])
def get_estacion(estacion_id):
    conn = sqlite3.connect('gasotrack.db') 
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.nombre, e.latitud, e.longitud, e.horario, e.tipo, 
               GROUP_CONCAT(c.nombre) as combustibles 
        FROM Estacion e
        JOIN EstacionCombustible ec ON e.id = ec.estacion_id
        JOIN Combustible c ON ec.combustible_id = c.id
        WHERE e.id = ?
        GROUP BY e.id
    """, (estacion_id,))
    estacion = cursor.fetchone()
    conn.close()

    if estacion is None:
        return jsonify({'error': 'Estación no encontrada'}), 404

    resultado = {
        'id': estacion['id'],
        'nombre': estacion['nombre'],
        'latitud': estacion['latitud'],
        'longitud': estacion['longitud'],
        'horario': estacion['horario'],
        'tipo': estacion['tipo'],
        'combustibles': estacion['combustibles'].split(',')
    }
    return jsonify(resultado)

# Endpoint para crear un reporte
@app.route('/reportes', methods=['POST'])
def crear_reporte():
    conn = sqlite3.connect('gasotrack.db') 
    cursor = conn.cursor()
    data = request.get_json()
    estacion_id = data.get('estacion_id')
    combustible_id = data.get('combustible_id')
    disponibilidad = data.get('disponibilidad')

    # Validar datos
    if not estacion_id or not combustible_id or disponibilidad not in ['Sí', 'No']:
        return jsonify({'error': 'Datos inválidos'}), 400

    # Crear nuevo reporte
    cursor.execute("""
        INSERT INTO Reporte (estacion_id, combustible_id, disponibilidad)
        VALUES (?, ?, ?)
    """, (estacion_id, combustible_id, disponibilidad))
    conn.commit()
    conn.close() 

    return jsonify({'mensaje': 'Reporte creado exitosamente'}), 201

# Endpoint para obtener estadísticas
@app.route('/estadisticas', methods=['GET'])
def get_estadisticas():
    conn = sqlite3.connect('gasotrack.db') 
    cursor = conn.cursor()

    # Calcular estadísticas (ejemplo básico)
    cursor.execute("SELECT COUNT(*) FROM Estacion")
    total_estaciones = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Reporte WHERE disponibilidad = 'Sí'")
    estaciones_con_combustible = cursor.fetchone()[0]
    conn.close()

    porcentaje_disponibilidad = (estaciones_con_combustible / total_estaciones) * 100 if total_estaciones > 0 else 0

    # Puedes agregar más estadísticas aquí, como disponibilidad por tipo de combustible, etc.

    estadisticas = {
        'porcentaje_disponibilidad': porcentaje_disponibilidad,
        'total_estaciones': total_estaciones,
        'estaciones_con_combustible': estaciones_con_combustible
    }
    return jsonify(estadisticas)

if __name__ == '__main__':
    app.run(debug=True)
