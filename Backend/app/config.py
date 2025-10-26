import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-dificil'
    
    # A linha abaixo foi comentada para não tentar conectar ao banco
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost'

    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'outra-chave-secreta-para-jwt'

    # Define que o token de acesso expira em 1 dia
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)