import requests
from datetime import datetime

# Cache simples em memória
cache = {}
CACHE_TIMEOUT_SECONDS = 3600

def is_cache_valid(key):
    if key not in cache: return False
    entry_time = cache[key]['timestamp']
    return (datetime.now() - entry_time).total_seconds() < CACHE_TIMEOUT_SECONDS

def fallback_indicadores(cache_key):
    if cache_key in cache and cache[cache_key]:
        return cache[cache_key]['data']
    else:
        return {"selic": "10,50%", "cdi": "10,40%", "selic_valor": 0.1050, "cdi_valor": 0.1040, "data_referencia": "fallback"}

def get_indicadores_mercado():
    cache_key = 'indicadores'
    if is_cache_valid(cache_key): return cache[cache_key]['data']
    try:
        url = "https://brasilapi.com.br/api/taxas/v1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dados_taxas = response.json()
        selic_info = next((taxa for taxa in dados_taxas if taxa['nome'] == 'Selic'), None)
        cdi_info = next((taxa for taxa in dados_taxas if taxa['nome'] == 'CDI'), None)
        if not selic_info or not cdi_info: raise ValueError("Dados de SELIC ou CDI não encontrados")
        taxa_selic_anual = selic_info['valor'] / 100
        taxa_cdi_anual = cdi_info['valor'] / 100
        data_referencia = datetime.now().strftime('%Y-%m-%d')
        resultado = {"selic": f"{taxa_selic_anual:.2%}", "cdi": f"{taxa_cdi_anual:.2%}", "selic_valor": taxa_selic_anual, "cdi_valor": taxa_cdi_anual, "data_referencia": data_referencia}
        cache[cache_key] = {'data': resultado, 'timestamp': datetime.now()}
        return resultado
    except (requests.RequestException, ValueError) as e:
        print(f"AVISO: Falha ao buscar dados da BrasilAPI: {e}.")
        return fallback_indicadores(cache_key)

def calcular_aliquota_ir(dias):
    if dias <= 180: return 0.225
    elif dias <= 360: return 0.20
    elif dias <= 720: return 0.175
    else: return 0.15

# Em services.py, substitua a função inteira por esta:

def _get_tesouro_data():
    cache_key = 'tesouro_direto_titulos'
    if is_cache_valid(cache_key): return cache[cache_key]['data']
    try:
        # URL ATUALIZADA para a nova API do Tesouro Direto
        url = "https://www.tesourodireto.com.br/proxy/tesouro-direto-web/api/v1/titulos/selecao"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # LÓGICA ATUALIZADA para ler a nova estrutura de dados
        dados_api = response.json()['response']
        
        # A estrutura agora é um dicionário, então convertemos para uma lista
        lista_titulos = dados_api.get('listaDeTitulos', [])
        
        # Criamos um formato compatível com o que o resto do código espera
        formatted_data = {
            "response": {
                "TrsrBdTradgList": []
            }
        }
        for titulo in lista_titulos:
            bond_data = titulo.get('titulo', {})
            formatted_data["response"]["TrsrBdTradgList"].append({
                "TrsrBd": {
                    "nm": bond_data.get('nome'),
                    "anulInvstmtRate": bond_data.get('taxaRendimento'),
                    "invstmtStbl": "A" # Assumindo como disponível
                }
            })
        
        cache[cache_key] = {'data': formatted_data, 'timestamp': datetime.now()}
        return formatted_data
        
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"AVISO: Falha ao buscar dados do Tesouro Direto: {e}.")
        print("Usando DADOS MOCKADOS para o Tesouro Direto.")
        # O fallback com dados mockados continua sendo uma boa prática
        return {"response": {"TrsrBdTradgList": [{"TrsrBd": {"nm": "Tesouro Selic 2029 (Mock)", "anulInvstmtRate": 0.0035, "invstmtStbl": "A"}}]}}
    

def simular_cdb(valor_inicial, prazo_dias, percentual_cdi):
    indicadores = get_indicadores_mercado()
    if "erro" in indicadores: return indicadores
    taxa_cdi_anual = indicadores['cdi_valor']
    fator_cdi = percentual_cdi / 100.0
    taxa_rendimento_anual = taxa_cdi_anual * fator_cdi
    taxa_rendimento_periodo = (1 + taxa_rendimento_anual)**(prazo_dias / 365) - 1
    rendimento_bruto = valor_inicial * taxa_rendimento_periodo
    valor_bruto = valor_inicial + rendimento_bruto
    aliquota_ir = calcular_aliquota_ir(prazo_dias)
    valor_ir = rendimento_bruto * aliquota_ir
    valor_liquido = valor_bruto - valor_ir
    resultado = {
        "tipo_investimento": f"CDB {percentual_cdi}% CDI",
        "valor_investido": f"R$ {valor_inicial:,.2f}", "prazo_dias": prazo_dias, "taxa_utilizada": f"{percentual_cdi}% da CDI ({indicadores['cdi']})",
        "rendimento_bruto": f"R$ {rendimento_bruto:,.2f}", "aliquota_ir": f"{aliquota_ir:.1%}", "valor_ir": f"R$ {valor_ir:,.2f}", "valor_liquido_final": f"R$ {valor_liquido:,.2f}"
    }
    resultado['_raw_values'] = {"valor_inicial": valor_inicial, "valor_liquido_final": valor_liquido}
    return resultado

def simular_lci_lca(valor_inicial, prazo_dias, percentual_cdi):
    indicadores = get_indicadores_mercado()
    if "erro" in indicadores: return indicadores
    taxa_cdi_anual = indicadores['cdi_valor']
    fator_cdi = percentual_cdi / 100.0
    taxa_rendimento_anual = taxa_cdi_anual * fator_cdi
    taxa_rendimento_periodo = (1 + taxa_rendimento_anual)**(prazo_dias / 365) - 1
    rendimento_liquido = valor_inicial * taxa_rendimento_periodo
    valor_final = valor_inicial + rendimento_liquido
    resultado = {
        "tipo_investimento": f"LCI/LCA {percentual_cdi}% CDI",
        "valor_investido": f"R$ {valor_inicial:,.2f}", "prazo_dias": prazo_dias, "taxa_utilizada": f"{percentual_cdi}% da CDI ({indicadores['cdi']})",
        "rendimento_bruto": f"R$ {rendimento_liquido:,.2f}", "aliquota_ir": "Isento", "valor_ir": "R$ 0,00", "valor_liquido_final": f"R$ {valor_final:,.2f}"
    }
    resultado['_raw_values'] = {"valor_inicial": valor_inicial, "valor_liquido_final": valor_final}
    return resultado

def simular_tesouro_selic(valor_inicial, prazo_dias):
    dados_tesouro = _get_tesouro_data()
    if not dados_tesouro: return {"erro": "Não foi possível obter os dados dos títulos."}
    titulo_selic = next((t['TrsrBd'] for t in dados_tesouro['response']['TrsrBdTradgList'] if "Tesouro Selic" in t['TrsrBd']['nm'] and t['TrsrBd']['invstmtStbl'] == 'A'), None)
    if not titulo_selic: return {"erro": "Título Tesouro Selic não encontrado."}
    indicadores = get_indicadores_mercado()
    if "erro" in indicadores: return indicadores
    taxa_selic_anual = indicadores['selic_valor']
    taxa_rendimento_anual = taxa_selic_anual + titulo_selic['anulInvstmtRate']
    taxa_rendimento_periodo = (1 + taxa_rendimento_anual)**(prazo_dias / 365) - 1
    rendimento_bruto = valor_inicial * taxa_rendimento_periodo
    aliquota_ir = calcular_aliquota_ir(prazo_dias)
    valor_ir = rendimento_bruto * aliquota_ir
    taxa_b3_anual = 0.0020
    taxa_b3_periodo = (taxa_b3_anual / 365) * prazo_dias
    valor_taxa_b3 = ((valor_inicial + (valor_inicial + rendimento_bruto)) / 2) * taxa_b3_periodo
    valor_liquido_final = (valor_inicial + rendimento_bruto) - valor_ir - valor_taxa_b3
    resultado = {
        "tipo_investimento": titulo_selic['nm'],
        "valor_investido": f"R$ {valor_inicial:,.2f}", "prazo_dias": prazo_dias, "taxa_utilizada": f"SELIC ({indicadores['selic']}) + {titulo_selic['anulInvstmtRate']:.4f}%",
        "rendimento_bruto": f"R$ {rendimento_bruto:,.2f}", "aliquota_ir": f"{aliquota_ir:.1%}", "valor_ir": f"R$ {valor_ir:,.2f}", "taxa_b3": f"R$ {valor_taxa_b3:,.2f} (0,20% a.a.)", "valor_liquido_final": f"R$ {valor_liquido_final:,.2f}"
    }
    resultado['_raw_values'] = {"valor_inicial": valor_inicial, "valor_liquido_final": valor_liquido_final}
    return resultado