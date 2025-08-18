# InvestEasy - Simulador de Investimentos em Renda Fixa

InvestEasy é uma aplicação web focada na simulação e no cálculo de investimentos em renda fixa, permitindo que os usuários entendam a rentabilidade de diferentes produtos de forma simples e direta.

## ✨ Funcionalidades Principais

* **Autenticação de Usuários:** Sistema completo de cadastro e login para uma experiência personalizada.
* **Simulação de Investimentos:**
    * Cálculo detalhado para **CDB/RDB** com base no percentual do CDI.
    * (Em desenvolvimento) Simulação para LCI/LCA (isentos de IR) e Títulos do Tesouro Direto.
* **Indicadores em Tempo Real:** Consulta automática das taxas CDI e SELIC através da API pública do Banco Central do Brasil, garantindo cálculos sempre atualizados.
* **Interface Integrada:** O back-end serve tanto a API de dados quanto a interface do usuário, criando uma aplicação web coesa e fácil de executar.

## 💻 Tecnologias Utilizadas

* **Backend:**
    * **Python 3**
    * **Flask:** Microframework para a construção da API e o serviço das páginas.
    * **Flask-SQLAlchemy:** ORM para interação com o banco de dados.
    * **Flask-JWT-Extended:** Para autenticação baseada em tokens.
    * **MySQL:** Banco de dados relacional para armazenamento dos usuários.

* **Frontend:**
    * HTML5
    * CSS3
    * JavaScript (Vanilla)

## 📂 Estrutura do Projeto

Este projeto utiliza uma estrutura de **monorepo**, onde o código do back-end e do front-end residem no mesmo repositório para facilitar o gerenciamento, mas mantendo uma separação lógica de pastas.

```
PROJETO_4/
|
|-- .vscode/
|   └── settings.json       # Configurações do VS Code para o projeto
|
|-- Backend/                # Contém toda a lógica do servidor Flask
|   |-- app/
|   |-- venv/
|   |-- config.py
|   |-- requirements.txt
|   └── run.py
|
|-- frontend/               # Contém os arquivos da interface do usuário
|   |-- static/
|   └── templates/
|
└── .gitignore              # Ignora arquivos desnecessários de ambos os projetos
```

## 🚀 Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

* Git
* Python 3.8+
* Um servidor MySQL em execução (ex: via MySQL Workbench)

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd PROJETO_4
    ```

2.  **Configure o Ambiente do Backend:**
    * Navegue até a pasta do backend:
      ```bash
      cd Backend
      ```
    * Crie e ative o ambiente virtual:
      ```bash
      # Criar o venv
      python -m venv venv
      # Ativar no Windows (PowerShell)
      .\venv\Scripts\activate
      ```
    * Instale as dependências:
      ```bash
      pip install -r requirements.txt
      ```

3.  **Configure o Banco de Dados:**
    * Abra seu cliente MySQL (Workbench, etc.) e crie o banco de dados:
      ```sql
      CREATE DATABASE investeasy_db;
      ```
    * No arquivo `Backend/app/config.py`, ajuste a linha `SQLALCHEMY_DATABASE_URI` com a **sua senha** do MySQL.

4.  **Crie as Tabelas no Banco:**
    * Certifique-se de que seu `venv` está ativo no terminal, dentro da pasta `Backend`.
    * Inicie o shell do Python: `python`
    * Execute os seguintes comandos:
      ```python
      from app import create_app, db
      app = create_app()
      with app.app_context():
          db.create_all()
      exit()
      ```

## ▶️ Como Executar a Aplicação

1.  Navegue até a pasta do backend no terminal:
    ```bash
    cd Backend
    ```
2.  Ative o ambiente virtual (se ainda não estiver ativo):
    ```bash
    .\venv\Scripts\activate
    ```
3.  Inicie o servidor Flask:
    ```bash
    python run.py
    ```
4.  Abra seu navegador e acesse: `http://127.0.0.1:5000`

## 🌐 Endpoints da API

A aplicação expõe os seguintes endpoints de API (além de servir as páginas `/` e `/resultados`):

* `POST /api/registrar`: Cria um novo usuário.
* `POST /api/login`: Autentica um usuário e retorna um token JWT.
* `GET /api/indicadores`: Retorna as taxas CDI e SELIC atuais.
* `POST /api/simular/cdb`: (Requer autenticação) Simula um investimento em CDB.

---
