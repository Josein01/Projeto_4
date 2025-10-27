import os
from dotenv import load_dotenv
from app import create_app, db
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

# 1️⃣ Carrega variáveis do arquivo .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "easy_invest")

# Cria o app Flask
app = create_app()

# 2️⃣ Cria um engine temporário para garantir que o banco exista
temp_engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}")

try:
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        print(f"✅ Banco de dados '{DB_NAME}' criado/verificado com sucesso!")
except OperationalError as e:
    print(f"❌ Erro ao conectar ao MySQL: {e}")

# 3️⃣ Configura o SQLAlchemy para usar o banco correto
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# 4️⃣ Reconfigura o SQLAlchemy dentro do contexto do Flask
with app.app_context():
    try:
        # Fecha conexões antigas
        db.engine.dispose()

        # Cria novo engine vinculado ao banco correto
        new_engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])

        # Reatribui a sessão
        db.session.remove()
        db.session = scoped_session(sessionmaker(bind=new_engine))

        # Cria as tabelas no banco (se não existirem)
        with new_engine.begin() as conn:
            db.metadata.create_all(conn)

        print(f"✅ Conexão reconfigurada com sucesso para o banco '{DB_NAME}'.")
    except Exception as e:
        print(f"❌ Erro ao reconfigurar o SQLAlchemy: {e}")

# 5️⃣ Inicializa o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)
