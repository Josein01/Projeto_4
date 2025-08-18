# Backend/config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-dificil'
    
    # A linha abaixo foi comentada para não tentar conectar ao banco
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:sua_senha@localhost/investeasy_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'outra-chave-secreta-para-jwt'