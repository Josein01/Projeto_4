import os
from datetime import timedelta
from dotenv import load_dotenv

# Nota: O run.py já deve carregar o .env, mas adicionamos aqui
# por segurança, caso este arquivo seja importado por outro script.
# Ele busca o .env na pasta pai (Backend/)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-dificil'
    
    # ==========================================================
    # AQUI ESTÁ A CORREÇÃO
    # ==========================================================
    
    # Pega as variáveis de ambiente do arquivo .env
    USER = os.environ.get('DB_USER')
    PASS = os.environ.get('DB_PASS')
    HOST = os.environ.get('DB_HOST')
    NAME = os.environ.get('DB_NAME')
    
    # Monta a string de conexão (URI) dinamicamente
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASS}@{HOST}/{NAME}'
    
    # ==========================================================
    # FIM DA CORREÇÃO
    # ==========================================================

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'outra-chave-secreta-para-jwt'

    # Define que o token de acesso expira em 1 dia
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)