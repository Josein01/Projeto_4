# Backend/app/routes.py
from flask import render_template, current_app, request, jsonify
from sqlalchemy import func
from app.models import User, Calculo, Investimento
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import services
import decimal

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
    user_id = get_jwt_identity()
    kpis = db.session.query(func.count(Calculo.idcalculos), func.sum(Calculo.valor), func.sum(Calculo.resultadocalculo)).filter(Calculo.usuario_idusuario == user_id).first()
    distribuicao = db.session.query(Investimento.tipoinvestimento, func.count(Calculo.idcalculos)).join(Investimento).filter(Calculo.usuario_idusuario == user_id).group_by(Investimento.tipoinvestimento).all()
    ultima_simulacao = db.session.query(Calculo, Investimento).join(Investimento).filter(Calculo.usuario_idusuario == user_id).order_by(Calculo.idcalculos.desc()).first()
    dashboard_data = {
        "kpi_principais": { "total_simulacoes": kpis[0] or 0, "total_investido": f"R$ {kpis[1]:,.2f}" if kpis[1] else "R$ 0,00", "retorno_liquido_total": f"R$ {(kpis[2] or 0) - (kpis[1] or 0):,.2f}" if kpis[2] else "R$ 0,00" },
        "distribuicao_investimentos": [{"tipo": tipo, "quantidade": qtd} for tipo, qtd in distribuicao],
        "ultima_simulacao": None
    }
    if ultima_simulacao:
        calculo, investimento = ultima_simulacao
        rendimento_bruto = calculo.resultadocalculo - calculo.valor
        dashboard_data["ultima_simulacao"] = { "tipo_investimento": investimento.tipoinvestimento, "valor_investido": f"R$ {calculo.valor:,.2f}", "prazo": f"{calculo.prazo} dias", "taxa_utilizada": calculo.taxa, "rendimento_bruto": f"R$ {rendimento_bruto:,.2f}", "valor_liquido": f"R$ {calculo.resultadocalculo:,.2f}" }
    return jsonify(dashboard_data)