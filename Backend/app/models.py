from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'usuario'
    
    idusuario = db.Column(db.Integer, primary_key=True)
    nomeusuario = db.Column(db.String(15), nullable=False)
    sobrenomeusuario = db.Column(db.String(100), nullable=False)
    emailusuario = db.Column(db.String(100), unique=True, index=True, nullable=False)
    senhausuario = db.Column(db.String(300), nullable=False)
    calculos = db.relationship('Calculo', backref='autor', lazy='dynamic')

    def set_password(self, password):
        self.senhausuario = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senhausuario, password)

class Calculo(db.Model):
    __tablename__ = 'calculos'

    idcalculos = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    prazo = db.Column(db.Integer, nullable=False)
    taxa = db.Column(db.String(45), nullable=False)
    resultadocalculo = db.Column(db.Numeric(20, 2), nullable=False)
    tipo_investimento = db.Column(db.String(45))
    data_calculo = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    usuario_idusuario = db.Column(db.Integer, db.ForeignKey('usuario.idusuario'))