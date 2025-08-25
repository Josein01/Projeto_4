// =======================================================================
// ARQUIVO: script.js (Página da Calculadora)
// RESPONSABILIDADE: Controlar a lógica da página principal de simulação.
// =======================================================================

// --- Estado da Aplicação ---
let selectedCalculation = "CDB/RDB";

// --- Elementos do DOM ---
const optionButtons = document.querySelectorAll(".option-button");
const calculateButton = document.getElementById("calculate-btn");

/**
 * Função de inicialização principal.
 */
function init() {
  optionButtons.forEach((button) => {
    button.addEventListener("click", function () {
      optionButtons.forEach((btn) => btn.classList.remove("selected"));
      this.classList.add("selected");
      selectedCalculation = this.getAttribute("data-option");
    });
  });

  calculateButton.addEventListener("click", () => {
    const investmentValue = document.getElementById("investment-value").value;
    const timePeriod = document.getElementById("time-period").value;
    const cdiPercentage = document.getElementById("cdi-percentage").value;
    performCalculation(selectedCalculation, investmentValue, timePeriod, cdiPercentage);
  });

  fetchMarketIndicators();
}

/**
 * Função "guardiã": Verifica se a resposta da API é um erro de autenticação.
 * Se for um erro 401 ou 422 (comum para token expirado/inválido), redireciona para o login.
 * @param {Response} response - O objeto de resposta do fetch.
 */
function handleAuthError(response) {
    if (response.status === 401 || response.status === 422) {
        localStorage.removeItem('accessToken'); // Limpa o token inválido
        alert("Sua sessão expirou. Por favor, faça o login novamente.");
        window.location.href = '/login';
        return true; // Indica que um erro de autenticação ocorreu
    }
    return false;
}

/**
 * Busca os indicadores de mercado da API.
 */
async function fetchMarketIndicators() {
  try {
    const response = await fetch('/api/indicadores');
    if (!response.ok) throw new Error('Falha ao buscar indicadores.');
    const data = await response.json();
    document.getElementById("cdi-rate").textContent = data.cdi;
    document.getElementById("cdi-update").textContent = new Date(data.data_referencia).toLocaleDateString('pt-BR');
    document.getElementById("selic-rate").textContent = data.selic;
    document.getElementById("selic-update").textContent = new Date(data.data_referencia).toLocaleDateString('pt-BR');
  } catch (error) {
    console.error('Erro:', error);
  }
}

/**
 * Função principal que realiza o cálculo.
 */
async function performCalculation(type, value, period, cdiPercent) {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    alert('Você precisa estar logado para realizar uma simulação.');
    window.location.href = '/login';
    return;
  }
  
  let apiUrl = '';
  let simulationData = {};

  if (type === 'CDB/RDB' || type === 'LCI/LCA') {
    apiUrl = (type === 'CDB/RDB') ? '/api/simular/cdb' : '/api/simular/lci-lca';
    simulationData = {
      valor_inicial: parseFloat(value),
      prazo_dias: parseInt(period),
      percentual_cdi: parseFloat(cdiPercent)
    };
  } else if (type === 'Tesouro Direito') {
    apiUrl = '/api/simular/tesouro-selic';
    simulationData = {
      valor_inicial: parseFloat(value),
      prazo_dias: parseInt(period)
    };
  } else {
    return;
  }

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(simulationData)
    });

    // Chama a função "guardiã" para verificar o token
    if (handleAuthError(response)) return;

    const result = await response.json();
    if (!response.ok) throw new Error(result.erro || 'Erro na simulação.');

    localStorage.setItem('simulationResult', JSON.stringify(result));
    window.location.href = '/resultados';

  } catch (error) {
    alert(error.message);
  }
}

document.addEventListener("DOMContentLoaded", init);