// frontend/static/script2.js

document.addEventListener('DOMContentLoaded', () => {
    const resultDataString = localStorage.getItem('simulationResult');

    if (!resultDataString) {
        window.location.href = '/';
        return;
    }

    const resultData = JSON.parse(resultDataString);

    // --- LEITURA SIMPLIFICADA (SEM "dados_entrada" ou "resultados") ---
    document.getElementById('tipo-investimento').textContent = resultData.tipo_investimento;
    document.getElementById('valor-investido').textContent = resultData.valor_investido;
    document.getElementById('prazo-dias').textContent = resultData.prazo_dias;
    document.getElementById('taxa-utilizada').textContent = resultData.taxa_utilizada;
    document.getElementById('rendimento-bruto').textContent = resultData.rendimento_bruto;
    document.getElementById('aliquota-ir').textContent = resultData.aliquota_ir;
    document.getElementById('valor-ir').textContent = resultData.valor_ir;
    document.getElementById('valor-liquido').textContent = resultData.valor_liquido_final;
    
    // As lógicas para taxa_b3 e comparativo continuam funcionando da mesma forma
});

function newSimulation() {
    localStorage.removeItem('simulationResult');
    window.location.href = '/';
}