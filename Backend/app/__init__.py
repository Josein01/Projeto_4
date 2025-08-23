import os
from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# --- CONFIGURAÇÃO DE CAMINHOS CUSTOMIZADOS ---
app_folder_path = os.path.abspath(os.path.dirname(__file__))
project_root_path = os.path.join(app_folder_path, '..', '..')
TEMPLATE_FOLDER = os.path.join(project_root_path, 'frontend', 'templates')
STATIC_FOLDER = os.path.join(project_root_path, 'frontend', 'static')

# --- INICIALIZAÇÃO DAS EXTENSÕES ---
db = SQLAlchemy() 
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class=Config):
    """
    Cria e configura a instância da aplicação Flask.
    """
    app = Flask(__name__,
                template_folder=TEMPLATE_FOLDER,
                static_folder=STATIC_FOLDER)
    
    app.config.from_object(config_class)

    db.init_app(app) 
    bcrypt.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from . import routes

    return app