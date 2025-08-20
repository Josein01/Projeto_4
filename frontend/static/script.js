// State management
let selectedCalculation = "CDB/RDB"

// DOM elements
const optionButtons = document.querySelectorAll(".option-button")
const calculateButton = document.getElementById("calculate-btn")

// Função de inicialização
function init() {
  // Configura os eventos de clique nos botões de opção
  optionButtons.forEach((button) => {
    button.addEventListener("click", function () {
      optionButtons.forEach((btn) => btn.classList.remove("selected"))
      this.classList.add("selected")
      selectedCalculation = this.getAttribute("data-option")
    })
  })

  // Configura o evento de clique no botão de calcular
  calculateButton.addEventListener("click", () => {
    const investmentValue = document.getElementById("investment-value").value
    const timePeriod = document.getElementById("time-period").value
    const cdiPercentage = document.getElementById("cdi-percentage").value

    // Chama a função que se comunica com o back-end
    performCalculation(selectedCalculation, investmentValue, timePeriod, cdiPercentage)
  })

  // [MODIFICADO] Busca os indicadores reais da API ao carregar a página
  fetchMarketIndicators()
}

/**
 * [NOVO] Busca os indicadores de mercado (CDI/SELIC) da nossa API.
 */
async function fetchMarketIndicators() {
  try {
    const response = await fetch('/api/indicadores');
    if (!response.ok) throw new Error('Falha ao buscar indicadores.');
    
    const data = await response.json();

    // Atualiza a tela com os dados recebidos do back-end
    document.getElementById("cdi-rate").textContent = data.cdi;
    document.getElementById("cdi-update").textContent = new Date(data.data_referencia).toLocaleDateString('pt-BR');
    document.getElementById("selic-rate").textContent = data.selic;
    document.getElementById("selic-update").textContent = new Date(data.data_referencia).toLocaleDateString('pt-BR');
  } catch (error) {
    console.error('Erro:', error);
  }
}

/**
 * [MODIFICADO] Envia os dados para o back-end e processa a simulação.
 */
async function performCalculation(type, value, period, cdiPercent) {
  // Verifica se o usuário está logado buscando o token
  const token = localStorage.getItem('accessToken');
  if (!token) {
    alert('Você precisa estar logado para realizar uma simulação.');
    window.location.href = '/login';
    return;
  }
  
  let apiUrl = '';
  let simulationData = {};

  // Define a URL da API e os dados a serem enviados
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
    return; // Se o tipo for desconhecido, não faz nada
  }

  try {
    // Faz a chamada POST para a API, enviando os dados e o token de autenticação
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(simulationData)
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.erro || 'Erro na simulação.');

    // Salva o resultado e redireciona para a página de resultados
    localStorage.setItem('simulationResult', JSON.stringify(result));
    window.location.href = '/resultados';

  } catch (error) {
    console.error('Erro na simulação:', error);
    alert(error.message);
  }
}

// Inicializa o script quando a página termina de carregar
document.addEventListener("DOMContentLoaded", init)