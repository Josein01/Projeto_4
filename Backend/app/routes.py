# Backend/app/routes.py
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
    
@current_app.route('/api/perfil', methods=['GET'])
@jwt_required()
def get_perfil():
    user_id = get_jwt_identity()
    usuario = User.query.get(user_id)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    user_data = {
        "primeiro_nome": usuario.nomeusuario,
        "sobrenome": usuario.sobrenomeusuario,
        "email": usuario.emailusuario
    }
    return jsonify(user_data)

@current_app.route('/api/perfil', methods=['PUT'])
@jwt_required()
def update_perfil():
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
    
# --- NOVAS APIS PARA ADICIONAR ---

@current_app.route('/api/alterar-senha', methods=['POST'])
@jwt_required()
def alterar_senha():
    """
    Permite que um usuário logado altere sua própria senha.
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

# --- Lógica para o Upload da Foto ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@current_app.route('/api/perfil/foto', methods=['POST'])
@jwt_required()
def upload_foto_perfil():
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
    user_id = get_jwt_identity()
    calculo = Calculo.query.filter_by(idcalculos=id_calculo, usuario_idusuario=user_id).first()
    if not calculo:
        return jsonify({"erro": "Registro de cálculo não encontrado."}), 404
    
    resultado_recriado = {
        "tipo_investimento": calculo.investimento.tipoinvestimento,
        "valor_investido": f"R$ {calculo.valor:,.2f}",
        "prazo_dias": calculo.prazo,
        "taxa_utilizada": calculo.taxa,
        "rendimento_bruto": "N/A (Histórico)",
        "aliquota_ir": "N/A (Histórico)",
        "valor_ir": "N/A (Histórico)",
        "valor_liquido_final": f"R$ {calculo.resultadocalculo:,.2f}"
    }
    return jsonify(resultado_recriado)

@current_app.route('/api/historico/<int:id_calculo>', methods=['DELETE'])
@jwt_required()
def delete_historico_item(id_calculo):
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
    dados = services.get_indicadores_mercado()
    if "erro" in dados: return jsonify(dados), 503
    return jsonify(dados)

@current_app.route('/api/simular/cdb', methods=['POST'])
@jwt_required()
def simular_investimento_cdb():
    dados_entrada = request.get_json()
    user_id = get_jwt_identity()
    resultado = services.simular_cdb(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado, 1)
    return jsonify(resultado)

@current_app.route('/api/simular/lci-lca', methods=['POST'])
@jwt_required()
def simular_investimento_lci_lca():
    dados_entrada = request.get_json()
    user_id = get_jwt_identity()
    resultado = services.simular_lci_lca(float(dados_entrada['valor_inicial']), int(dados_entrada['prazo_dias']), float(dados_entrada['percentual_cdi']))
    if "erro" not in resultado:
        salvar_calculo_no_historico(user_id, resultado, 2)
    return jsonify(resultado)

@current_app.route('/api/simular/tesouro-selic', methods=['POST'])
@jwt_required()
def simular_investimento_tesouro_selic():
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
    Busca e agrega os dados de todas as simulações do usuário
    para alimentar a tela de Dashboard, incluindo dados para gráficos.
    """
    user_id = get_jwt_identity()
    
    # Busca todos os cálculos para processamento, ordenados por data
    todos_calculos = db.session.query(Calculo).filter(Calculo.usuario_idusuario == user_id).order_by(Calculo.data_calculo.asc()).all()

    # --- Processamento para os Gráficos ---
    
    # 1. Dados para "Evolução do Investimento" (gráfico de linha)
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

    # 2. Dados para o "Comparativo Mensal" (gráfico de barras) - LÓGICA REAL
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
    
    # --- KPIs e Distribuição (código existente) ---
    kpis = db.session.query(func.count(Calculo.idcalculos), func.sum(Calculo.valor)).filter(Calculo.usuario_idusuario == user_id).first()
    distribuicao = db.session.query(Investimento.tipoinvestimento, func.count(Calculo.idcalculos)).join(Investimento).filter(Calculo.usuario_idusuario == user_id).group_by(Investimento.tipoinvestimento).all()
    
    # Pega os dados da última simulação para os cards de detalhe
    ultima_simulacao_dados = None
    if todos_calculos:
        ultima = todos_calculos[-1] # Pega o último item da lista já ordenada
        rendimento_bruto = ultima.resultadocalculo - ultima.valor # Aproximação
        ultima_simulacao_dados = {
            "valor_investido": f"R$ {ultima.valor:,.2f}",
            "prazo": f"{ultima.prazo} dias",
            "taxa_utilizada": ultima.taxa,
            "rendimento_bruto": f"R$ {rendimento_bruto:,.2f}",
            "valor_liquido": f"R$ {ultima.resultadocalculo:,.2f}"
        }

    dashboard_data = {
        "kpi_principais": {
            "total_simulacoes": kpis[0] or 0,
            "total_investido": f"R$ {kpis[1]:,.2f}" if kpis[1] else "R$ 0,00",
        },
        "distribuicao_investimentos": [{"tipo": tipo, "quantidade": qtd} for tipo, qtd in distribuicao],
        "evolucao_investimento": evolucao_data,
        "comparativo_mensal": comparativo_mensal_data,
        "ultima_simulacao": ultima_simulacao_dados
    }

    return jsonify(dashboard_data)