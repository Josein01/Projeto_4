from flask import render_template, current_app, request, jsonify
# from app.models import User # Comentado - Não usamos o modelo de usuário
# from app import db # Comentado - Não usamos o banco de dados
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import services

# --- ROTAS PARA SERVIR AS PÁGINAS DO FRONT-END ---

@current_app.route('/')
def home():
    return render_template('index.html')

@current_app.route('/login')
def login_page():
    return render_template('Login.html')

@current_app.route('/resultados')
def resultados_page():
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
    usuario_logado = get_jwt_identity()
    print(f"DEBUG: Simulação CDB pedida por: {usuario_logado}")
    dados_entrada = request.get_json()
    if not dados_entrada or not all(k in dados_entrada for k in ('valor_inicial', 'prazo_dias', 'percentual_cdi')): return jsonify({"erro": "Parâmetros obrigatórios ausentes."}), 400
    try:
        resultado = services.simular_cdb(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
        if "erro" in resultado: return jsonify(resultado), 503
        return jsonify(resultado)
    except (ValueError, TypeError):
        return jsonify({"erro": "Parâmetros inválidos."}), 400


@current_app.route('/api/simular/lci-lca', methods=['POST'])
@jwt_required()
def simular_investimento_lci_lca():
    usuario_logado = get_jwt_identity()
    print(f"DEBUG: Simulação LCI/LCA pedida por: {usuario_logado}")
    dados_entrada = request.get_json()
    if not dados_entrada or not all(k in dados_entrada for k in ('valor_inicial', 'prazo_dias', 'percentual_cdi')): return jsonify({"erro": "Parâmetros obrigatórios ausentes."}), 400
    try:
        resultado = services.simular_lci_lca(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
        if "erro" in resultado: return jsonify(resultado), 503
        return jsonify(resultado)
    except (ValueError, TypeError):
        return jsonify({"erro": "Parâmetros inválidos."}), 400