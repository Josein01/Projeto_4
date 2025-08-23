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

# --- ROTAS DA API COM LÓGICA DE BANCO DE DADOS REAL ---

@current_app.route('/api/registrar', methods=['POST'])
def registrar_usuario():
    dados = request.get_json()
    if not all(k in dados for k in ('email', 'senha', 'primeiro_nome', 'sobrenome')):
        return jsonify({'erro': 'Dados incompletos fornecidos'}), 400

    if User.query.filter_by(emailusuario=dados['email']).first():
        return jsonify({'erro': 'Este e-mail já está em uso'}), 409

    novo_usuario = User(
        nomeusuario=dados['primeiro_nome'],
        sobrenomeusuario=dados['sobrenome'],
        emailusuario=dados['email']
    )
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
    
    # --- DEPURAÇÃO ADICIONADA ---
    # Vamos verificar o tipo da identidade ANTES de criar o token
    user_identity = usuario.idusuario
    print(f"--- DEBUG LOGIN ---")
    print(f"ID do usuário: {user_identity}")
    print(f"Tipo do ID do usuário: {type(user_identity)}")
    
    # Convertemos para string
    user_identity_str = str(user_identity)
    print(f"ID convertido para string: {user_identity_str}")
    print(f"Tipo do ID convertido: {type(user_identity_str)}")
    print(f"-------------------")
    
    access_token = create_access_token(identity=user_identity_str)
    return jsonify(access_token=access_token)

# Função auxiliar para salvar o cálculo no histórico
def salvar_calculo_no_historico(user_id, resultado_simulacao):
    try:
        print(f"[DEBUG] salvando cálculo no histórico...")
        print(f"[DEBUG] user_id recebido: {user_id} (tipo: {type(user_id)})")

        dados_entrada = resultado_simulacao['dados_entrada']
        resultados = resultado_simulacao['resultados']
        
        # Extrai o valor numérico do resultado líquido
        valor_liquido_str = resultados['valor_liquido_final'].replace('R$ ', '').replace('.', '').replace(',', '.')
        
        novo_calculo = Calculo(
            usuario_idusuario=int(user_id),  # <-- garante que será inteiro
            valor=decimal.Decimal(
                dados_entrada['valor_investido']
                .replace('R$ ', '')
                .replace('.', '')
                .replace(',', '.')
            ),
            prazo=int(dados_entrada['prazo_dias']),
            taxa=dados_entrada['taxa_utilizada'],
            tipo_investimento=resultado_simulacao.get('tipo_investimento', 'N/A'),
            resultadocalculo=decimal.Decimal(valor_liquido_str)
        )

        db.session.add(novo_calculo)
        db.session.commit()
        print(f"[DEBUG] Histórico de cálculo salvo com sucesso para user_id={user_id}")

    except Exception as e:
        print(f"[ERRO] ao salvar histórico: {e} (user_id={user_id}, tipo={type(user_id)})")
        db.session.rollback()


@current_app.route('/api/indicadores', methods=['GET'])
def get_indicadores():
    dados = services.get_indicadores_mercado()
    if "erro" in dados: return jsonify(dados), 503
    return jsonify(dados)

@current_app.route('/api/simular/cdb', methods=['POST'])
@jwt_required()
def simular_investimento_cdb():
    print("\n--- INICIANDO DEBUG DA ROTA /api/simular/cdb ---")
    
    user_id = int(get_jwt_identity())  # <-- conversão aqui
    print(f"[DEBUG] Token válido. Identidade do usuário (int): {user_id}")

    dados_entrada = request.get_json()
    print(f"[DEBUG] JSON recebido do front-end: {dados_entrada}")

    if not dados_entrada:
        print("[ERRO] JSON não recebido.")
        return jsonify({"erro": "Nenhum dado recebido."}), 400

    try:
        valor = float(dados_entrada.get('valor_inicial'))
        dias = int(dados_entrada.get('prazo_dias'))
        percentual = float(dados_entrada.get('percentual_cdi'))
        print(f"[DEBUG] Dados convertidos com sucesso: valor={valor}, dias={dias}, percentual={percentual}")

        resultado = services.simular_cdb(valor, dias, percentual)
        print(f"[DEBUG] Resultado recebido do serviço: {resultado}")

        if "erro" in resultado:
            print(f"[ERRO] O serviço retornou um erro: {resultado['erro']}")
            return jsonify(resultado), 503
        
        salvar_calculo_no_historico(user_id, resultado)
        print("[DEBUG] Histórico salvo com sucesso.")
        
        print("--- FIM DO DEBUG ---")
        return jsonify(resultado)

    except (ValueError, TypeError, KeyError) as e:
        print(f"[ERRO FATAL] Falha ao processar os dados de entrada: {e}")
        print("--- FIM DO DEBUG ---")
        return jsonify({"erro": "Parâmetros inválidos ou faltando no JSON enviado."}), 400

@current_app.route('/api/simular/lci-lca', methods=['POST'])
@jwt_required()
def simular_investimento_lci_lca():
    user_id = int(get_jwt_identity())  # <-- conversão aqui
    dados_entrada = request.get_json()
    resultado = services.simular_lci_lca(
        float(dados_entrada['valor_inicial']),
        int(dados_entrada['prazo_dias']),
        float(dados_entrada['percentual_cdi'])
    )
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado)
    return jsonify(resultado)


@current_app.route('/api/simular/tesouro-selic', methods=['POST'])
@jwt_required()
def simular_investimento_tesouro_selic():
    user_id = int(get_jwt_identity())  # <-- conversão aqui
    dados_entrada = request.get_json()
    resultado = services.simular_tesouro_selic(
        float(dados_entrada['valor_inicial']),
        int(dados_entrada['prazo_dias'])
    )
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado)
    return jsonify(resultado)
# Adicione este código no final do arquivo Backend/app/routes.py

@current_app.route('/api/test-auth', methods=['GET'])
@jwt_required()
def test_auth():
    """
    Uma rota super simples que serve apenas para testar se o token JWT é válido.
    """
    try:
        # Apenas tenta pegar a identidade do usuário a partir do token
        user_id = get_jwt_identity()
        print(f"[DEBUG ROTA DE TESTE] Token válido para o usuário: {user_id}")
        return jsonify(logged_in_as=user_id), 200
    except Exception as e:
        print(f"[DEBUG ROTA DE TESTE] Ocorreu um erro: {e}")
        return jsonify(error=str(e)), 500
