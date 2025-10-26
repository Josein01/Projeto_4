from sqlalchemy import create_engine, text
from app import create_app, db

app = create_app()

with app.app_context():
    # 1️⃣ Cria uma conexão genérica só pro servidor MySQL (sem schema)
    temp_engine = create_engine("mysql+pymysql://root:@localhost")

    # 2️⃣ Cria o schema se não existir
    with temp_engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS easy_invest"))
        conn.commit()

    # 3️⃣ Atualiza a URI do app para o banco correto
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/easy_invest"

    # 4️⃣ Recria o engine e o metadata com o schema correto
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])

    with engine.begin() as conn:
        db.metadata.create_all(conn)

    print("✅ Banco de dados 'easy_invest' criado/verificado com sucesso!")

if __name__ == "__main__":
    app.run(debug=True)
