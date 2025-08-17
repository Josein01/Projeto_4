# app/routes.py

from flask import current_app, request, jsonify
from app.models import User
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import services

@current_app.route('/api')
def api_index():
    return jsonify({'mensagem': 'API do InvestEasy está no ar!'})

# --- ROTAS DE AUTENTICAÇÃO ---

@current_app.route('/api/registrar', methods=['POST'])
def registrar_usuario():
    dados = request.get_json()
    if not dados or not 'email' in dados or not 'senha' in dados:
        return jsonify({'erro': 'Dados incompletos fornecidos'}), 400
    if User.query.filter_by(email=dados['email']).first():
        return jsonify({'erro': 'Este e-mail já está em uso'}), 409
    novo_usuario = User(
        primeiro_nome=dados.get('primeiro_nome'),
        sobrenome=dados.get('sobrenome'),
        email=dados['email']
    )
    novo_usuario.set_password(dados['senha'])
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado com sucesso!'}), 201

@current_app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or not 'email' in dados or not 'senha' in dados:
        return jsonify({'erro': 'E-mail ou senha não fornecidos'}), 400
    usuario = User.query.filter_by(email=dados['email']).first()
    if usuario is None or not usuario.check_password(dados['senha']):
        return jsonify({'erro': 'Credenciais inválidas'}), 401
    access_token = create_access_token(identity=usuario.id)
    return jsonify(access_token=access_token)

@current_app.route('/api/recuperar-senha', methods=['POST'])
def recuperar_senha():
    # Lógica de recuperação de senha (placeholder)
    return jsonify({'mensagem': 'Se o e-mail estiver em nosso sistema, um link de recuperação será enviado.'})

# --- ROTAS DE DADOS E SIMULAÇÕES ---

@current_app.route('/api/indicadores', methods=['GET'])
def get_indicadores():
    dados = services.get_indicadores_mercado()
    if "erro" in dados:
        return jsonify(dados), 503
    return jsonify(dados)

@current_app.route('/api/simular/cdb', methods=['POST'])
@jwt_required()
def simular_investimento_cdb():
    dados_entrada = request.get_json()
    if not dados_entrada or not all(k in dados_entrada for k in ('valor_inicial', 'prazo_dias', 'percentual_cdi')):
        return jsonify({"erro": "Parâmetros obrigatórios ausentes."}), 400
    try:
        valor = float(dados_entrada['valor_inicial'])
        dias = int(dados_entrada['prazo_dias'])
        percentual = float(dados_entrada['percentual_cdi'])
        resultado = services.simular_cdb(valor, dias, percentual)
        if "erro" in resultado:
            return jsonify(resultado), 503
        return jsonify(resultado)
    except (ValueError, TypeError):
        return jsonify({"erro": "Parâmetros inválidos."}), 400