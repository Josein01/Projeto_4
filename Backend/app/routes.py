from flask import render_template, current_app, request, jsonify
# from app.models import User # Comentado - Não usamos o modelo de usuário
# from app import db # Comentado - Não usamos o banco de dados
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import services

# --- ROTAS PARA SERVIR AS PÁGINAS DO FRONT-END ---

@current_app.route('/')
@current_app.route('/Calculadora') # Mantemos /Calculadora para garantir que funcione
def home():
    """Esta rota servirá o arquivo index.html como página principal."""
    return render_template('index.html')

@current_app.route('/login')
def login_page():
    """Esta rota servirá a página Login.html."""
    return render_template('Login.html')

@current_app.route('/resultados')
def resultados_page():
    """Esta rota servirá a página Resultados.html."""
    return render_template('Resultados.html')

# --- ROTAS DA API (COM MOCK DE AUTENTICAÇÃO) ---

@current_app.route('/api/registrar', methods=['POST'])
def registrar_usuario():
    dados = request.get_json()
    print(f"DEBUG: Tentativa de registro (MOCK) com dados: {dados}")
    return jsonify({'mensagem': 'Usuário criado com sucesso! (MOCK)'}), 201

@current_app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or not 'email' in dados or not 'senha' in dados: 
        return jsonify({'erro': 'E-mail ou senha não fornecidos'}), 400
    print(f"DEBUG: Login simulado para o usuário: {dados['email']}")
    access_token = create_access_token(identity=dados['email'])
    return jsonify(access_token=access_token)

@current_app.route('/api/indicadores', methods=['GET'])
def get_indicadores():
    dados = services.get_indicadores_mercado()
    if "erro" in dados: return jsonify(dados), 503
    return jsonify(dados)

@current_app.route('/api/simular/cdb', methods=['POST'])
@jwt_required()
def simular_investimento_cdb():
    dados_entrada = request.get_json()
    if not all(k in dados_entrada for k in ('valor_inicial', 'prazo_dias', 'percentual_cdi')): return jsonify({"erro": "Parâmetros obrigatórios ausentes."}), 400
    try:
        resultado = services.simular_cdb(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
        if "erro" in resultado: return jsonify(resultado), 503
        return jsonify(resultado)
    except (ValueError, TypeError):
        return jsonify({"erro": "Parâmetros inválidos."}), 400

@current_app.route('/api/simular/lci-lca', methods=['POST'])
@jwt_required()
def simular_investimento_lci_lca():
    dados_entrada = request.get_json()
    if not all(k in dados_entrada for k in ('valor_inicial', 'prazo_dias', 'percentual_cdi')): return jsonify({"erro": "Parâmetros obrigatórios ausentes."}), 400
    try:
        resultado = services.simular_lci_lca(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
        if "erro" in resultado: return jsonify(resultado), 503
        return jsonify(resultado)
    except (ValueError, TypeError):
        return jsonify({"erro": "Parâmetros inválidos."}), 400

# --- NOVA ROTA ADICIONADA ---
@current_app.route('/api/simular/tesouro-selic', methods=['POST'])
@jwt_required()
def simular_investimento_tesouro_selic():
    dados_entrada = request.get_json()
    # Note que Tesouro Selic não precisa do 'percentual_cdi'
    if not all(k in dados_entrada for k in ('valor_inicial', 'prazo_dias')):
        return jsonify({"erro": "Parâmetros 'valor_inicial' e 'prazo_dias' são obrigatórios."}), 400
    try:
        resultado = services.simular_tesouro_selic(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']))
        if "erro" in resultado: return jsonify(resultado), 503
        return jsonify(resultado)
    except (ValueError, TypeError):
        return jsonify({"erro": "Parâmetros inválidos."}), 400