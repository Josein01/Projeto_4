from app import create_app, db
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

app = create_app()

# 1️⃣ Cria uma conexão temporária SEM banco selecionado (para garantir a criação)
temp_engine = create_engine("mysql+pymysql://root:@localhost")

try:
    with temp_engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS easy_invest"))
        print("✅ Banco de dados 'easy_invest' criado/verificado com sucesso!")
except OperationalError as e:
    print(f"❌ Erro ao conectar ao MySQL: {e}")

# 2️⃣ Atualiza a URI do SQLAlchemy para usar o banco correto
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/easy_invest"

# 3️⃣ Reconfigura o SQLAlchemy dentro do contexto da aplicação Flask
with app.app_context():
    try:
        # Fecha conexões antigas
        db.engine.dispose()

        # Cria um novo engine e vincula à sessão
        new_engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        db.session.remove()
        db.session = scoped_session(sessionmaker(bind=new_engine))

        # Cria as tabelas no banco se não existirem
        with new_engine.begin() as conn:
            db.metadata.create_all(conn)

        print("✅ Conexão reconfigurada com sucesso para o banco 'easy_invest'.")
    except Exception as e:
        print(f"❌ Erro ao reconfigurar o SQLAlchemy: {e}")

# 4️⃣ Inicializa o servidor Flask normalmente
if __name__ == "__main__":
    app.run(debug=True)
