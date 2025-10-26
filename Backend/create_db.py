from app import create_app, db
from sqlalchemy import text

app = create_app()

# Script para criação automática do banco de dados completo
with app.app_context():
    # 1️⃣ Cria o schema principal
    db.engine.execute(text("""
        CREATE DATABASE IF NOT EXISTS easy_invest
        DEFAULT CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
    """))

    # 2️⃣ Usa o schema criado
    db.engine.execute(text("USE easy_invest;"))

    # 3️⃣ Cria tabela de investimentos
    db.engine.execute(text("""
        CREATE TABLE IF NOT EXISTS investimento (
            idinvestimento INT NOT NULL AUTO_INCREMENT,
            tipoinvestimento VARCHAR(45) NOT NULL,
            PRIMARY KEY (idinvestimento)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    # 4️⃣ Cria tabela de usuários
    db.engine.execute(text("""
        CREATE TABLE IF NOT EXISTS usuario (
            idusuario INT NOT NULL AUTO_INCREMENT,
            nomeusuario VARCHAR(15) NOT NULL,
            sobrenomeusuario VARCHAR(100) NOT NULL,
            emailusuario VARCHAR(100) NOT NULL,
            senhausuario VARCHAR(300) NOT NULL,
            fotoperfil VARCHAR(255) NULL DEFAULT NULL,
            PRIMARY KEY (idusuario)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    # 5️⃣ Cria tabela de cálculos
    db.engine.execute(text("""
        CREATE TABLE IF NOT EXISTS calculos (
            idcalculos INT NOT NULL AUTO_INCREMENT,
            valor DECIMAL(10,0) NOT NULL,
            prazo INT NOT NULL,
            taxa VARCHAR(20) NOT NULL,
            resultadocalculo DECIMAL(20,0) NOT NULL,
            data_calculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            usuario_idusuario INT NOT NULL,
            investimento_idinvestimento INT NOT NULL,
            PRIMARY KEY (idcalculos),
            INDEX fk_calculos_usuario1_idx (usuario_idusuario ASC),
            INDEX fk_calculos_investimento1_idx (investimento_idinvestimento ASC),
            CONSTRAINT fk_calculos_investimento1
                FOREIGN KEY (investimento_idinvestimento)
                REFERENCES investimento (idinvestimento),
            CONSTRAINT fk_calculos_usuario1
                FOREIGN KEY (usuario_idusuario)
                REFERENCES usuario (idusuario)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    # 6️⃣ Cria tabela de indicadores
    db.engine.execute(text("""
        CREATE TABLE IF NOT EXISTS indicadores (
            idindicadores INT NOT NULL AUTO_INCREMENT,
            tipoindicadores VARCHAR(45) NOT NULL,
            taxaanual VARCHAR(45) NOT NULL,
            dataatualiza DATETIME NOT NULL,
            PRIMARY KEY (idindicadores)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """))

    print("✅ Banco de dados 'easy_invest' e todas as tabelas foram criadas com sucesso!")
