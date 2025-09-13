// frontend/static/script2.js (VERSÃO ATUALIZADA)

document.addEventListener('DOMContentLoaded', () => {
    const resultDataString = localStorage.getItem('simulationResult');

    if (!resultDataString) {
        // Se não houver resultado, volta para a página inicial
        window.location.href = '/';
        return;
    }

    const resultData = JSON.parse(resultDataString);

    // Preenche os campos principais que sempre existem
    document.getElementById('tipo-investimento').textContent = resultData.tipo_investimento;
    document.getElementById('valor-investido').textContent = resultData.valor_investido;
    document.getElementById('prazo-dias').textContent = resultData.prazo_dias;
    document.getElementById('taxa-utilizada').textContent = resultData.taxa_utilizada;
    document.getElementById('rendimento-bruto').textContent = resultData.rendimento_bruto;
    document.getElementById('aliquota-ir').textContent = resultData.aliquota_ir;
    document.getElementById('valor-ir').textContent = resultData.valor_ir;
    document.getElementById('valor-liquido').textContent = resultData.valor_liquido_final;

    // =======================================================================
    // == LÓGICA ADICIONADA PARA EXIBIR O COMPARATIVO CONDICIONALMENTE ==
    // =======================================================================
    const comparativoSection = document.getElementById('comparativo-section');

    // Verifica se os dados do comparativo existem no objeto de resultado
    if (resultData.comparativo_valor) {
        // Se existirem, preenche os campos do comparativo
        document.getElementById('comparativo-valor').textContent = resultData.comparativo_valor;
        document.getElementById('comparativo-diferenca-rs').textContent = resultData.comparativo_diferenca_rs;
        document.getElementById('comparativo-diferenca-perc').textContent = resultData.comparativo_diferenca_perc;

        // E o mais importante: torna a seção visível
        comparativoSection.style.display = 'block';
    } else {
        // Se não existirem (ex: para LCI/LCA), garante que a seção permaneça oculta
        comparativoSection.style.display = 'none';
    }
});

/**
 * Limpa o resultado salvo e volta para a página inicial.
 */
function newSimulation() {
    localStorage.removeItem('simulationResult');
    window.location.href = '/';
}