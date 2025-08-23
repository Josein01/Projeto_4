# Backend/app/routes.py
from flask import render_template, current_app, request, jsonify
from app.models import User, Calculo
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import services
import decimal

# --- ROTAS DE PÁGINAS ---
@current_app.route('/')
def home(): return render_template('index.html')

@current_app.route('/login')
def login_page(): return render_template('Login.html')

@current_app.route('/resultados')
def resultados_page(): return render_template('Resultados.html')

@current_app.route('/historico')
def historico_page(): return render_template('Historico.html')

# --- ROTAS DA API COM LÓGICA DE BANCO DE DADOS REAL ---

@current_app.route('/api/registrar', methods=['POST'])
def registrar_usuario():
    dados = request.get_json()
    if not all(k in dados for k in ('email', 'senha', 'primeiro_nome', 'sobrenome')):
        return jsonify({'erro': 'Dados incompletos fornecidos'}), 400
    if User.query.filter_by(emailusuario=dados['email']).first():
        return jsonify({'erro': 'Este e-mail já está em uso'}), 409
    novo_usuario = User(nomeusuario=dados['primeiro_nome'], sobrenomeusuario=dados['sobrenome'], emailusuario=dados['email'])
    novo_usuario.set_password(dados['senha'])
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado com sucesso!'}), 201

@current_app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not all(k in dados for k in ('email', 'senha')): 
        return jsonify({'erro': 'E-mail ou senha não fornecidos'}), 400
    usuario = User.query.filter_by(emailusuario=dados['email']).first()
    if usuario is None or not usuario.check_password(dados['senha']):
        return jsonify({'erro': 'Credenciais inválidas'}), 401
    access_token = create_access_token(identity=str(usuario.idusuario))
    return jsonify(access_token=access_token)

# Função auxiliar para salvar o cálculo no histórico
def salvar_calculo_no_historico(user_id, resultado_simulacao, tipo_invest_id):
    try:
        # Pega os dados numéricos puros que foram adicionados no services.py
        raw_values = resultado_simulacao['_raw_values']
        
        novo_calculo = Calculo(
            usuario_idusuario=int(user_id),
            investimento_idinvestimento=tipo_invest_id,
            valor=decimal.Decimal(raw_values['valor_inicial']),
            prazo=int(resultado_simulacao['prazo_dias']),
            taxa=resultado_simulacao['taxa_utilizada'],
            resultadocalculo=decimal.Decimal(raw_values['valor_liquido_final'])
        )
        db.session.add(novo_calculo)
        db.session.commit()
        print(f"DEBUG: Histórico de cálculo salvo para o usuário ID: {user_id}")
    except Exception as e:
        print(f"ERRO ao salvar histórico: {e}")
        db.session.rollback()

@current_app.route('/api/indicadores', methods=['GET'])
def get_indicadores():
    dados = services.get_indicadores_mercado()
    if "erro" in dados: return jsonify(dados), 503
    return jsonify(dados)

# --- ROTAS DE SIMULAÇÃO ---
@current_app.route('/api/simular/cdb', methods=['POST'])
@jwt_required()
def simular_investimento_cdb():
    dados_entrada = request.get_json()
    user_id = get_jwt_identity()
    resultado = services.simular_cdb(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado, 1) # ID 1 = CDB/RDB
    return jsonify(resultado)

@current_app.route('/api/simular/lci-lca', methods=['POST'])
@jwt_required()
def simular_investimento_lci_lca():
    dados_entrada = request.get_json()
    user_id = get_jwt_identity()
    resultado = services.simular_lci_lca(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado, 2) # ID 2 = LCI/LCA
    return jsonify(resultado)

@current_app.route('/api/simular/tesouro-selic', methods=['POST'])
@jwt_required()
def simular_investimento_tesouro_selic():
    dados_entrada = request.get_json()
    user_id = get_jwt_identity()
    resultado = services.simular_tesouro_selic(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']))
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado, 3) # ID 3 = Tesouro Selic
    return jsonify(resultado)