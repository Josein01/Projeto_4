from flask import render_template, current_app, request, jsonify
from sqlalchemy import func
from app.models import User, Calculo, Investimento
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import services
import decimal
from sqlalchemy import func, extract
import os
from werkzeug.utils import secure_filename
from flask import url_for
from datetime import datetime

# --- ROTAS DE PÁGINAS ---
@current_app.route('/')
def home():
    return render_template('index.html')

@current_app.route('/login')
def login_page():
    return render_template('Login.html')

@current_app.route('/resultados')
def resultados_page():
    return render_template('Resultados.html')

@current_app.route('/perfil')
@jwt_required(optional=True)
def perfil_page():
    return render_template('Perfil.html')

# --- ROTAS DA API ---

@current_app.route('/api/registrar', methods=['POST'])
def registrar_usuario():
    """
    Registra um novo usuário no sistema.
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        description: Dados para o cadastro do novo usuário.
        schema:
          type: object
          required: [email, senha, primeiro_nome, sobrenome]
          properties:
            email:
              type: string
              example: "novo.usuario@exemplo.com"
            senha:
              type: string
              example: "senhaForte123"
            primeiro_nome:
              type: string
              example: "Maria"
            sobrenome:
              type: string
              example: "Silva"
    responses:
      201:
        description: Usuário criado com sucesso!
      400:
        description: Dados incompletos fornecidos.
      409:
        description: O e-mail fornecido já está em uso.
    """
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
    """
    Autentica um usuário e retorna um token de acesso.
    Esta rota recebe as credenciais do usuário (e-mail e senha) e, se forem válidas,
    gera um token JWT que deve ser usado para autenticar as próximas requisições.
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        description: Credenciais do usuário para login.
        schema:
          type: object
          required: [email, senha]
          properties:
            email:
              type: string
              example: "usuario@exemplo.com"
            senha:
              type: string
              example: "123456"
    responses:
      200:
        description: Login bem-sucedido.
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      401:
        description: Credenciais inválidas ou dados não fornecidos.
    """
    dados = request.get_json()
    if not all(k in dados for k in ('email', 'senha')):
        return jsonify({'erro': 'E-mail ou senha não fornecidos'}), 401
    usuario = User.query.filter_by(emailusuario=dados['email']).first()
    if usuario is None or not usuario.check_password(dados['senha']):
        return jsonify({'erro': 'Credenciais inválidas'}), 401
    access_token = create_access_token(identity=str(usuario.idusuario))
    return jsonify(access_token=access_token)

@current_app.route('/api/perfil', methods=['GET'])
@jwt_required()
def get_perfil():
    """
    Busca os dados do perfil do usuário autenticado.
    Esta rota requer um token JWT válido no cabeçalho de autorização.
    ---
    tags:
      - Perfil do Usuário
    security:
      - bearerAuth: []
    responses:
      200:
        description: Dados do perfil retornados com sucesso.
        schema:
          type: object
          properties:
            primeiro_nome:
              type: string
              example: "João"
            sobrenome:
              type: string
              example: "Silva"
            email:
              type: string
              example: "joao.silva@exemplo.com"
      401:
        description: Token de autorização ausente ou inválido.
      404:
        description: Usuário não encontrado.
    """
    user_id = get_jwt_identity()
    usuario = User.query.get(user_id)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    user_data = {
        "primeiro_nome": usuario.nomeusuario,
        "sobrenome": usuario.sobrenomeusuario,
        "email": usuario.emailusuario,
        "foto_url": url_for('static', filename=f'profile_pics/{usuario.fotoperfil}', _external=True) if usuario.fotoperfil else None
    }
    return jsonify(user_data)

@current_app.route('/api/perfil', methods=['PUT'])
@jwt_required()
def update_perfil():
    """
    Atualiza as informações do perfil do usuário.
    Permite alterar o primeiro nome e/ou o sobrenome do usuário autenticado.
    ---
    tags:
      - Perfil do Usuário
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        description: Campos a serem atualizados. Pelo menos um campo deve ser fornecido.
        schema:
          type: object
          properties:
            primeiro_nome:
              type: string
              example: "Maria"
            sobrenome:
              type: string
              example: "Souza"
    responses:
      200:
        description: Perfil atualizado com sucesso!
      401:
        description: Token de autorização ausente ou inválido.
      404:
        description: Usuário não encontrado.
    """
    user_id = get_jwt_identity()
    usuario = User.query.get(user_id)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido"}), 400
    if 'primeiro_nome' in dados:
        usuario.nomeusuario = dados['primeiro_nome']
    if 'sobrenome' in dados:
        usuario.sobrenomeusuario = dados['sobrenome']
    db.session.commit()
    return jsonify({"mensagem": "Perfil atualizado com sucesso!"})

@current_app.route('/api/perfil', methods=['DELETE'])
@jwt_required()
def delete_perfil():
    """
    Apaga o perfil do usuário autenticado.
    Esta ação é irreversível e apaga todos os dados associados ao usuário.
    ---
    tags:
      - Perfil do Usuário
    security:
      - bearerAuth: []
    responses:
      200:
        description: Sua conta foi apagada com sucesso.
      401:
        description: Token de autorização ausente ou inválido.
      404:
        description: Usuário não encontrado.
      500:
        description: Erro interno ao apagar a conta.
    """
    user_id = get_jwt_identity()
    usuario = User.query.get(user_id)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    try:
        Calculo.query.filter_by(usuario_idusuario=user_id).delete()
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"mensagem": "Sua conta foi apagada com sucesso."})
    except Exception as e:
        db.session.rollback()
        print(f"ERRO ao deletar perfil: {e}")
        return jsonify({"erro": "Ocorreu um erro ao apagar sua conta."}), 500

@current_app.route('/api/alterar-senha', methods=['POST'])
@jwt_required()
def alterar_senha():
    """
    Altera a senha do usuário autenticado.
    ---
    tags:
      - Perfil do Usuário
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [senha_atual, nova_senha]
          properties:
            senha_atual:
              type: string
              format: password
              example: "senhaAntiga123"
            nova_senha:
              type: string
              format: password
              example: "senhaNova456"
    responses:
      200:
        description: Senha alterada com sucesso!
      400:
        description: Senhas não fornecidas.
      401:
        description: Senha atual incorreta ou token inválido.
    """
    user_id = get_jwt_identity()
    usuario = User.query.get(user_id)
    dados = request.get_json()
    senha_atual = dados.get('senha_atual')
    nova_senha = dados.get('nova_senha')
    if not senha_atual or not nova_senha:
        return jsonify({"erro": "Senha atual e nova senha são obrigatórias."}), 400
    if not usuario.check_password(senha_atual):
        return jsonify({"erro": "A senha atual está incorreta."}), 401
    usuario.set_password(nova_senha)
    db.session.commit()
    return jsonify({"mensagem": "Senha alterada com sucesso!"})

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@current_app.route('/api/perfil/foto', methods=['POST'])
@jwt_required()
def upload_foto_perfil():
    """
    Faz o upload da foto de perfil do usuário.
    ---
    tags:
      - Perfil do Usuário
    security:
      - bearerAuth: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: foto
        type: file
        required: true
        description: O arquivo de imagem para upload (png, jpg, jpeg).
    responses:
      200:
        description: Foto atualizada!
      400:
        description: Nenhum arquivo enviado ou formato inválido.
      401:
        description: Token de autorização ausente ou inválido.
    """
    user_id = get_jwt_identity()
    usuario = User.query.get(user_id)
    if 'foto' not in request.files: return jsonify({"erro": "Nenhum arquivo enviado"}), 400
    file = request.files['foto']
    if file.filename == '' or not allowed_file(file.filename): return jsonify({"erro": "Arquivo inválido"}), 400

    filename = secure_filename(f"user_{user_id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
    upload_folder = os.path.join(current_app.static_folder, 'profile_pics')
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    usuario.fotoperfil = filename
    db.session.commit()
    photo_url = url_for('static', filename=f'profile_pics/{filename}')
    return jsonify({"mensagem": "Foto atualizada!", "photo_url": photo_url})

@current_app.route('/api/historico', methods=['GET'])
@jwt_required()
def get_historico():
    """
    Busca o histórico de cálculos do usuário autenticado.
    ---
    tags:
      - Histórico
    security:
      - bearerAuth: []
    responses:
      200:
        description: Lista do histórico de cálculos.
      401:
        description: Token de autorização ausente ou inválido.
    """
    user_id = get_jwt_identity()
    calculos_do_usuario = db.session.query(Calculo, Investimento).join(Investimento).filter(Calculo.usuario_idusuario == user_id).order_by(Calculo.idcalculos.desc()).all()
    historico_list = []
    for calculo, investimento in calculos_do_usuario:
        historico_list.append({
            'id_calculo': calculo.idcalculos,
            'tipo_investimento': investimento.tipoinvestimento,
            'valor_investido': f"R$ {calculo.valor:,.2f}",
            'prazo_dias': calculo.prazo,
            'taxa_utilizada': calculo.taxa,
            'resultado_liquido': f"R$ {calculo.resultadocalculo:,.2f}",
            'data_calculo': calculo.data_calculo.strftime('%d/%m/%Y às %H:%M') if hasattr(calculo, 'data_calculo') and calculo.data_calculo else ''
        })
    return jsonify(historico_list)

@current_app.route('/api/historico/<int:id_calculo>', methods=['GET'])
@jwt_required()
def get_historico_item(id_calculo):
    """
    Busca um item específico do histórico de cálculo.
    ---
    tags:
      - Histórico
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id_calculo
        type: integer
        required: true
        description: O ID do cálculo a ser buscado.
    responses:
      200:
        description: Detalhes do cálculo.
      401:
        description: Token de autorização ausente ou inválido.
      404:
        description: Registro de cálculo não encontrado.
    """
    user_id = get_jwt_identity()
    calculo = Calculo.query.filter_by(idcalculos=id_calculo, usuario_idusuario=user_id).first()
    if not calculo:
        return jsonify({"erro": "Registro de cálculo não encontrado."}), 404

    resultado_recriado = {
        "tipo_investimento": calculo.investimento.tipoinvestimento,
        "valor_investido": f"R$ {calculo.valor:,.2f}",
        "prazo_dias": calculo.prazo,
        "taxa_utilizada": calculo.taxa,
        "valor_liquido_final": f"R$ {calculo.resultadocalculo:,.2f}"
    }
    return jsonify(resultado_recriado)

@current_app.route('/api/historico/<int:id_calculo>', methods=['DELETE'])
@jwt_required()
def delete_historico_item(id_calculo):
    """
    Apaga um item específico do histórico de cálculo.
    ---
    tags:
      - Histórico
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: id_calculo
        type: integer
        required: true
        description: O ID do cálculo a ser apagado.
    responses:
      200:
        description: Simulação deletada do histórico.
      401:
        description: Token de autorização ausente ou inválido.
      404:
        description: Registro de cálculo não encontrado.
    """
    user_id = get_jwt_identity()
    calculo_para_deletar = Calculo.query.filter_by(idcalculos=id_calculo, usuario_idusuario=user_id).first()
    if not calculo_para_deletar:
        return jsonify({"erro": "Registro de cálculo não encontrado."}), 404
    try:
        db.session.delete(calculo_para_deletar)
        db.session.commit()
        return jsonify({"mensagem": "Simulação deletada do histórico."})
    except Exception as e:
        db.session.rollback()
        print(f"ERRO ao deletar item do histórico: {e}")
        return jsonify({"erro": "Ocorreu um erro ao deletar o registro."}), 500

def salvar_calculo_no_historico(user_id, resultado_simulacao, tipo_invest_id):
    try:
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
    except Exception as e:
        print(f"ERRO ao salvar histórico: {e}")
        db.session.rollback()

@current_app.route('/api/indicadores', methods=['GET'])
def get_indicadores():
    """
    Busca os indicadores de mercado atuais (CDI e SELIC).
    ---
    tags:
      - Dados de Mercado
    responses:
      200:
        description: Indicadores retornados com sucesso.
      503:
        description: Serviço indisponível (falha ao buscar dados da API externa).
    """
    dados = services.get_indicadores_mercado()
    if "erro" in dados: return jsonify(dados), 503
    return jsonify(dados)

@current_app.route('/api/simular/cdb', methods=['POST'])
@jwt_required()
def simular_investimento_cdb():
    """
    Executa uma simulação de investimento para CDB.
    Recebe os parâmetros da simulação e retorna o resultado detalhado.
    ---
    tags:
      - Simulações
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        description: Parâmetros para a simulação de CDB.
        schema:
          type: object
          required: [valor_inicial, prazo_dias, percentual_cdi]
          properties:
            valor_inicial:
              type: number
              example: 10000.00
            prazo_dias:
              type: integer
              example: 730
            percentual_cdi:
              type: number
              example: 115.0
    responses:
      200:
        description: Resultado da simulação.
      401:
        description: Token de autorização ausente ou inválido.
    """
    dados_entrada = request.get_json()
    user_id = get_jwt_identity()
    resultado = services.simular_cdb(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado, 1)
    return jsonify(resultado)

@current_app.route('/api/simular/lci-lca', methods=['POST'])
@jwt_required()
def simular_investimento_lci_lca():
    """
    Executa uma simulação de investimento para LCI/LCA.
    ---
    tags:
      - Simulações
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [valor_inicial, prazo_dias, percentual_cdi]
          properties:
            valor_inicial:
              type: number
              example: 5000.00
            prazo_dias:
              type: integer
              example: 365
            percentual_cdi:
              type: number
              example: 98.0
    responses:
      200:
        description: Resultado da simulação.
      401:
        description: Token de autorização ausente ou inválido.
    """
    dados_entrada = request.get_json()
    user_id = get_jwt_identity()
    resultado = services.simular_lci_lca(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado, 2)
    return jsonify(resultado)

@current_app.route('/api/simular/tesouro-selic', methods=['POST'])
@jwt_required()
def simular_investimento_tesouro_selic():
    """
    Executa uma simulação de investimento para Tesouro Selic.
    ---
    tags:
      - Simulações
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [valor_inicial, prazo_dias]
          properties:
            valor_inicial:
              type: number
              example: 2500.00
            prazo_dias:
              type: integer
              example: 1095
    responses:
      200:
        description: Resultado da simulação.
      401:
        description: Token de autorização ausente ou inválido.
    """
    dados_entrada = request.get_json()
    user_id = get_jwt_identity()
    resultado = services.simular_tesouro_selic(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']))
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado, 3)
    return jsonify(resultado)

@current_app.route('/api/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """
    Busca e agrega todos os dados para a página de Dashboard.
    ---
    tags:
      - Dashboard
    security:
      - bearerAuth: []
    responses:
      200:
        description: Dados consolidados para o dashboard.
      401:
        description: Token de autorização ausente ou inválido.
    """
    user_id = get_jwt_identity()
    todos_calculos = db.session.query(Calculo).filter(Calculo.usuario_idusuario == user_id).order_by(Calculo.data_calculo.asc()).all()

    evolucao_data = []
    valor_investido_acumulado = 0
    valor_liquido_acumulado = 0
    for calculo in todos_calculos:
        valor_investido_acumulado += float(calculo.valor)
        valor_liquido_acumulado += float(calculo.resultadocalculo)
        evolucao_data.append({
            "data": calculo.data_calculo.strftime('%d/%m/%Y'),
            "investido": round(valor_investido_acumulado, 2),
            "liquido": round(valor_liquido_acumulado, 2)
        })

    comparativo_mensal_query = db.session.query(
        extract('year', Calculo.data_calculo).label('ano'),
        extract('month', Calculo.data_calculo).label('mes'),
        func.sum(Calculo.valor).label('total_investido'),
        func.sum(Calculo.resultadocalculo - Calculo.valor).label('total_rendimento')
    ).filter(Calculo.usuario_idusuario == user_id).group_by('ano', 'mes').order_by('ano', 'mes').all()

    comparativo_mensal_data = {
        "labels": [f"{int(mes):02d}/{int(ano)}" for ano, mes, _, _ in comparativo_mensal_query],
        "investido": [float(total_investido) for _, _, total_investido, _ in comparativo_mensal_query],
        "rendimento": [float(total_rendimento) for _, _, _, total_rendimento in comparativo_mensal_query]
    }

    kpis = db.session.query(func.count(Calculo.idcalculos), func.sum(Calculo.valor)).filter(Calculo.usuario_idusuario == user_id).first()
    distribuicao = db.session.query(Investimento.tipoinvestimento, func.count(Calculo.idcalculos)).join(Investimento).filter(Calculo.usuario_idusuario == user_id).group_by(Investimento.tipoinvestimento).all()

    ultima_simulacao_dados = None
    if todos_calculos:
        ultima = todos_calculos[-1]
        rendimento_bruto_decimal = ultima.resultadocalculo - ultima.valor
        aliquota_ir = services.calcular_aliquo