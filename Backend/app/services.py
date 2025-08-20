# Backend/app/services.py

import requests
from datetime import datetime

# Cache simples em memória para evitar chamadas repetidas à API externa
cache = {}
CACHE_TIMEOUT_SECONDS = 3600 # 1 hora

def is_cache_valid(key):
    """Verifica se um item no cache ainda é válido."""
    if key not in cache:
        return False
    
    entry_time = cache[key]['timestamp']
    return (datetime.now() - entry_time).total_seconds() < CACHE_TIMEOUT_SECONDS



def get_indicadores_mercado():
    """Busca as taxas CDI e Selic da API do Banco Central com cache e fallback."""
    cache_key = 'indicadores'
    
    if is_cache_valid(cache_key):
        return cache[cache_key]['data']

    try:
        # FAZENDO DUAS CHAMADAS SEPARADAS E MAIS ROBUSTAS
        
        # 1. Busca o CDI (Série 12)
        url_cdi = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/1?formato=json"
        response_cdi = requests.get(url_cdi, timeout=5)
        response_cdi.raise_for_status()
        dados_cdi = response_cdi.json()
        if not dados_cdi:
            raise ValueError("Resposta da API do CDI veio vazia.")

        # 2. Busca a SELIC (Série 11)
        url_selic = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json"
        response_selic = requests.get(url_selic, timeout=5)
        response_selic.raise_for_status()
        dados_selic = response_selic.json()
        if not dados_selic:
            raise ValueError("Resposta da API da SELIC veio vazia.")
            
        cdi_info = dados_cdi[0]
        selic_info = dados_selic[0]
        
        # Ambas as taxas são diárias, então precisam ser anualizadas.
        taxa_cdi_anual = ((1 + float(cdi_info['valor']) / 100) ** 252) - 1
        taxa_selic_anual = ((1 + float(selic_info['valor']) / 100) ** 252) - 1

        resultado = {
            "selic": f"{taxa_selic_anual:.2%}",
            "cdi": f"{taxa_cdi_anual:.2%}",
            "selic_valor": taxa_selic_anual,
            "cdi_valor": taxa_cdi_anual,
            "data_referencia": datetime.strptime(cdi_info['data'], '%d/%m/%Y').strftime('%Y-%m-%d')
        }
        
        cache[cache_key] = {'data': resultado, 'timestamp': datetime.now()}
        return resultado

    except (requests.RequestException, ValueError) as e:
        print(f"AVISO: Falha ao buscar dados do BCB: {e}. Usando fallback.")
        if cache_key in cache:
            return cache[cache_key]['data']
        else:
            # Se a API falhar e não tivermos cache, retornamos um erro claro
            return {"erro": "Não foi possível obter os dados de mercado."}
        
def calcular_aliquota_ir(dias):
    """Calcula a alíquota do Imposto de Renda com base na tabela regressiva."""
    if dias <= 180: return 0.225
    elif dias <= 360: return 0.20
    elif dias <= 720: return 0.175
    else: return 0.15

def simular_cdb(valor_inicial, prazo_dias, percentual_cdi):
    """Realiza a simulação de um investimento em CDB."""
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
    return {
        "tipo_investimento": f"CDB {percentual_cdi}% CDI",
        "dados_entrada": { "valor_investido": f"R$ {valor_inicial:,.2f}", "prazo_dias": prazo_dias, "taxa_utilizada": f"{percentual_cdi}% da CDI ({indicadores['cdi']})" },
        "resultados": { "rendimento_bruto": f"R$ {rendimento_bruto:,.2f}", "aliquota_ir": f"{aliquota_ir:.1%}", "valor_ir": f"R$ {valor_ir:,.2f}", "valor_liquido_final": f"R$ {valor_liquido:,.2f}" }
    }

def simular_lci_lca(valor_inicial, prazo_dias, percentual_cdi):
    """Realiza a simulação de um investimento em LCI/LCA (isento de IR)."""
    indicadores = get_indicadores_mercado()
    if "erro" in indicadores: return indicadores
    taxa_cdi_anual = indicadores['cdi_valor']
    fator_cdi = percentual_cdi / 100.0
    taxa_rendimento_anual = taxa_cdi_anual * fator_cdi
    taxa_rendimento_periodo = (1 + taxa_rendimento_anual)**(prazo_dias / 365) - 1
    rendimento_liquido = valor_inicial * taxa_rendimento_periodo
    valor_final = valor_inicial + rendimento_liquido
    return {
        "tipo_investimento": f"LCI/LCA {percentual_cdi}% CDI",
        "dados_entrada": { "valor_investido": f"R$ {valor_inicial:,.2f}", "prazo_dias": prazo_dias, "taxa_utilizada": f"{percentual_cdi}% da CDI ({indicadores['cdi']})" },
        "resultados": { "rendimento_bruto": f"R$ {rendimento_liquido:,.2f}", "aliquota_ir": "Isento", "valor_ir": "R$ 0,00", "valor_liquido_final": f"R$ {valor_final:,.2f}" }
    }

def simular_tesouro_selic(valor_inicial, prazo_dias):
    """Realiza a simulação de um investimento no Tesouro Selic."""
    cache_key = 'tesouro_direto_titulos'
    dados_tesouro = None
    if is_cache_valid(cache_key):
        dados_tesouro = cache[cache_key]['data']
    else:
        try:
            url = "https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            dados_api = response.json()
            cache[cache_key] = {'data': dados_api, 'timestamp': datetime.now()}
            dados_tesouro = dados_api
        except (requests.RequestException, ValueError) as e:
            print(f"AVISO: Falha ao buscar dados do Tesouro Direto: {e}.")
            if cache_key in cache: dados_tesouro = cache[cache_key]['data']
            else: return {"erro": "Não foi possível obter os dados dos títulos do Tesouro Direto."}

    titulo_selic = next((t['TrsrBd'] for t in dados_tesouro['response']['TrsrBdTradgList'] if "Tesouro Selic" in t['TrsrBd']['nm'] and t['TrsrBd']['invstmtStbl'] == 'A'), None)
    if not titulo_selic:
        return {"erro": "Não foi possível encontrar um título Tesouro Selic disponível para investimento."}

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

    valor_final_bruto = valor_inicial + rendimento_bruto
    valor_liquido = valor_final_bruto - valor_ir - valor_taxa_b3
    
    return {
        "tipo_investimento": titulo_selic['nm'],
        "dados_entrada": { "valor_investido": f"R$ {valor_inicial:,.2f}", "prazo_dias": prazo_dias, "taxa_utilizada": f"SELIC ({indicadores['selic']}) + {titulo_selic['anulInvstmtRate']:.4f}%" },
        "resultados": { "rendimento_bruto": f"R$ {rendimento_bruto:,.2f}", "aliquota_ir": f"{aliquota_ir:.1%}", "valor_ir": f"R$ {valor_ir:,.2f}", "taxa_b3": f"R$ {valor_taxa_b3:,.2f} (0,20% a.a.)", "valor_liquido_final": f"R$ {valor_liquido:,.2f}" }
    }