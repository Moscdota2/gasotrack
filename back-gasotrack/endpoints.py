from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gasotrack.db'
db = SQLAlchemy(app)

conn = sqlite3.connect('gasotrack.db')
cursor = conn.cursor()

# Definición de los modelos de datos (Asegúrate de tenerlos definidos en otro archivo o aquí mismo)
class Estacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    horario = db.Column(db.String(50))
    tipo = db.Column(db.String(20), nullable=False)

class Combustible(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    octanaje = db.Column(db.Integer)

class EstacionCombustible(db.Model):
    estacion_id = db.Column(db.Integer, db.ForeignKey('estacion.id'), primary_key=True)
    combustible_id = db.Column(db.Integer, db.ForeignKey('combustible.id'), primary_key=True)
    estacion = db.relationship('Estacion', backref=db.backref('combustibles_disponibles', lazy=True))
    combustible = db.relationship('Combustible', backref=db.backref('estaciones_disponibles', lazy=True))

class Reporte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estacion_id = db.Column(db.Integer, db.ForeignKey('estacion.id'), nullable=False)
    combustible_id = db.Column(db.Integer, db.ForeignKey('combustible.id'), nullable=False)
    fechahora = db.Column(db.DateTime, default=datetime.utcnow)
    disponibilidad = db.Column(db.String(3), nullable=False) 

    estacion = db.relationship('Estacion', backref=db.backref('reportes', lazy=True))
    combustible = db.relationship('Combustible', backref=db.backref('reportes', lazy=True))

# ...

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('gasotrack.db')
        g.db.row_factory = sqlite3.Row 

    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

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

# Endpoint para obtener todas las estaciones
@app.route('/estaciones-get', methods=['GET'])
def get_estaciones2():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT e.id, e.nombre, e.latitud, e.longitud, e.horario, e.tipo, 
               GROUP_CONCAT(c.nombre) as combustibles 
        FROM Estacion e
        JOIN EstacionCombustible ec ON e.id = ec.estacion_id
        JOIN Combustible c ON ec.combustible_id = c.id
        GROUP BY e.id
    """)
    estaciones = cursor.fetchall()

    resultado = []
    for estacion in estaciones:
        resultado.append({
            'id': estacion['id'],
            'nombre': estacion['nombre'],
            'latitud': estacion['latitud'],
            'longitud': estacion['longitud'],
            'horario': estacion['horario'],
            'tipo': estacion['tipo'],
            'combustibles': estacion['combustibles'].split(',')  # Convertir la cadena a una lista
        })
    return jsonify(resultado)

# Endpoint para obtener una estación por ID
@app.route('/estaciones', methods=['GET'])
def get_estaciones():
    conn = sqlite3.connect('gasotrack.db')  # Abrir conexión en el endpoint
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.nombre, e.latitud, e.longitud, e.horario, e.tipo, 
               GROUP_CONCAT(c.nombre) as combustibles 
        FROM Estacion e
        JOIN EstacionCombustible ec ON e.id = ec.estacion_id
        JOIN Combustible c ON ec.combustible_id = c.id
        GROUP BY e.id
    """)
    estaciones = cursor.fetchall()
    conn.close()  # Cerrar conexión al final del endpoint

    resultado = []
    for estacion in estaciones:
        resultado.append({
            'id': estacion['id'],
            'nombre': estacion['nombre'],
            'latitud': estacion['latitud'],
            'longitud': estacion['longitud'],
            'horario': estacion['horario'],
            'tipo': estacion['tipo'],
            'combustibles': estacion['combustibles'].split(',') 
        })
    return jsonify(resultado)

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
    # Ya no necesitamos crear las tablas aquí, se crean en stations_scrap.py
    app.run(debug=True)
