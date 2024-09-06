# Definición de los modelos de datos (Asegúrate de tenerlos definidos en otro archivo o aquí mismo)
from flask_sqlalchemy import SQLAlchemy
from endpoints import app
from datetime import datetime, timedelta

db = SQLAlchemy(app)

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
