# Backend/app/__init__.py

import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# --- CONFIGURAÇÃO DE CAMINHOS CUSTOMIZADOS ---

# Pega o caminho absoluto para a pasta 'app' onde este arquivo está
app_folder_path = os.path.abspath(os.path.dirname(__file__))

# Sobe dois níveis para chegar na raiz do projeto (PROJETO_4)
project_root_path = os.path.join(app_folder_path, '..', '..')

# Define os caminhos para as pastas do frontend
# O Flask vai procurar os HTMLs em 'PROJETO_4/frontend/templates/'
TEMPLATE_FOLDER = os.path.join(project_root_path, 'frontend', 'templates') # <--- ESTA LINHA FOI AJUSTADA
# O Flask vai procurar os arquivos estáticos em 'PROJETO_4/frontend/static/'
STATIC_FOLDER = os.path.join(project_root_path, 'frontend', 'static')


# --- INICIALIZAÇÃO DAS EXTENSÕES ---
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class=Config):
    """
    Cria e configura a instância da aplicação Flask.
    """
    # Agora passamos os caminhos customizados ao criar a aplicação Flask
    app = Flask(__name__,
                template_folder=TEMPLATE_FOLDER,
                static_folder=STATIC_FOLDER)
    
    app.config.from_object(config_class)

    # Inicializa as extensões com a aplicação
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Importa e registra as rotas (URLs) da nossa aplicação
    with app.app_context():
        from . import routes

    return app