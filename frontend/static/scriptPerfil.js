// =======================================================================
// ARQUIVO: scriptPerfil.js
// RESPONSABILIDADE: Controlar a lógica do painel do usuário (Perfil, Histórico, Dashboard).
// =======================================================================

/**
 * Função de inicialização principal.
 * É executada assim que a página HTML termina de carregar.
 */
document.addEventListener("DOMContentLoaded", () => {
  // Inicializa os ícones da biblioteca Lucide
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
  
  // Busca todos os dados necessários da API assim que a página carrega
  loadProfileData();
  loadHistoryData();
  loadDashboardData();
  
  // Configura todos os eventos de clique da página
  initializeEventListeners();
});

/**
 * Busca os dados agregados para o dashboard na API e preenche os elementos.
 */
async function loadDashboardData() {
  const token = localStorage.getItem('accessToken');
  if (!token) return;

  try {
    const response = await fetch('/api/dashboard', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.erro || 'Falha ao buscar dados do dashboard.');

    // Preenche os cards de estatísticas (assume que os IDs/classes existem no HTML)
    const totalInvestidoEl = document.querySelector('.stats-grid .stat-card:nth-child(1) .stat-value');
    if (totalInvestidoEl) totalInvestidoEl.textContent = data.kpi_principais.total_investido;

    if (data.ultima_simulacao) {
        const ultimaSimulacaoPrazoEl = document.querySelector('.stats-grid .stat-card:nth-child(2) .stat-value');
        const ultimaSimulacaoTaxaEl = document.querySelector('.stats-grid .stat-card:nth-child(3) .stat-value');
        const ultimaSimulacaoRendimentoEl = document.querySelector('.stats-grid .stat-card:nth-child(4) .stat-value');
        if (ultimaSimulacaoPrazoEl) ultimaSimulacaoPrazoEl.textContent = data.ultima_simulacao.prazo;
        if (ultimaSimulacaoTaxaEl) ultimaSimulacaoTaxaEl.textContent = data.ultima_simulacao.taxa_utilizada;
        if (ultimaSimulacaoRendimentoEl) ultimaSimulacaoRendimentoEl.textContent = data.ultima_simulacao.rendimento_bruto;
    }
    
    // Inicializa os gráficos com os dados recebidos
    initializeCharts(data);

  } catch (error) {
    console.error("Erro ao carregar dados do dashboard:", error);
  }
}

/**
 * Inicializa os gráficos do Chart.js com os dados da API.
 */
function initializeCharts(dashboardData) {
    // Gráfico de Pizza: Distribuição de Investimentos
    const pieChartCanvas = document.getElementById('pieChart');
    if (pieChartCanvas && dashboardData.distribuicao_investimentos) {
        const ctxPie = pieChartCanvas.getContext('2d');
        const tipos = dashboardData.distribuicao_investimentos.map(item => item.tipo);
        const quantidades = dashboardData.distribuicao_investimentos.map(item => item.quantidade);

        new Chart(ctxPie, {
            type: 'pie',
            data: {
                labels: tipos,
                datasets: [{
                    label: 'Quantidade de Simulações',
                    data: quantidades,
                    backgroundColor: ['#463b9e', '#6c51f7', '#a49fef', '#c3c0f5'],
                    hoverOffset: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}

/**
 * Busca os dados do perfil do usuário na API (/api/perfil) e preenche a página.
 */
async function loadProfileData() {
  const token = localStorage.getItem('accessToken');
  if (!token) { 
    alert("Sessão expirada. Por favor, faça o login novamente.");
    window.location.href = '/login'; 
    return; 
  }

  try {
    const response = await fetch('/api/perfil', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const profile = await response.json();
    if (!response.ok) throw new Error(profile.erro || 'Falha ao buscar dados do perfil.');

    const profileName = `${profile.primeiro_nome} ${profile.sobrenome}`;
    const profileInitials = `${profile.primeiro_nome.charAt(0)}${profile.sobrenome.charAt(0)}`;
    
    document.querySelector('.profile-name').textContent = profileName;
    document.querySelector('.profile-email').textContent = profile.email;
    document.querySelector('.avatar span').textContent = profileInitials;
    document.querySelector('.avatar-large span').textContent = profileInitials;
    
    document.getElementById('firstName').value = profile.primeiro_nome;
    document.getElementById('lastName').value = profile.sobrenome;
    document.getElementById('email').value = profile.email;

  } catch (error) {
    console.error("Erro ao carregar dados do perfil:", error);
    alert(error.message);
  }
}

/**
 * Busca o histórico de simulações na API (/api/historico) e renderiza na tela.
 */
async function loadHistoryData() {
  const token = localStorage.getItem('accessToken');
  if (!token) return;

  const emptyState = document.getElementById("empty-state");
  const historyContent = document.getElementById("history-content");
  const historyList = document.getElementById("history-list");

  try {
    const response = await fetch('/api/historico', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const history = await response.json();
    if (!response.ok) throw new Error(history.erro || 'Falha ao buscar histórico.');
    
    if (history.length === 0) {
      emptyState.style.display = "flex";
      historyContent.style.display = "none";
    } else {
      emptyState.style.display = "none";
      historyContent.style.display = "block";

      historyList.innerHTML = history.map(item => `
        <div class="history-item" id="history-item-${item.id_calculo}">
            <div class="history-item-content">
                <div class="history-item-info">
                    <p><strong>${item.tipo_investimento}</strong></p>
                    <p>${item.valor_investido} por ${item.prazo_dias} dias</p>
                    <p class="history-date">${item.data_calculo}</p>
                </div>
                <div class="history-item-actions">
                    <button class="btn btn-outline btn-sm" onclick='handleCopyCalculation(${JSON.stringify(item)})'><i data-lucide="copy"></i> Copiar</button>
                    <button class="btn btn-outline btn-sm" onclick="handleViewResult(${item.id_calculo})"><i data-lucide="eye"></i> Ver resultados</button>
                    <button class="btn btn-outline btn-sm" style="color: #dc2626;" onclick="handleDeleteCalculation(${item.id_calculo})">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </div>
        </div>
      `).join("");
      lucide.createIcons();
    }
  } catch (error) {
    console.error("Erro ao carregar histórico:", error);
    emptyState.style.display = "flex";
    historyContent.style.display = "none";
    emptyState.querySelector('h3').textContent = 'Erro ao carregar o histórico.';
  }
}

/**
 * Lida com o clique no botão de deletar um item do histórico.
 */
async function handleDeleteCalculation(idCalculo) {
    if (!confirm("Tem certeza que deseja apagar este item do histórico?")) {
        return;
    }
    const token = localStorage.getItem('accessToken');
    if (!token) return;
    try {
        const response = await fetch(`/api/historico/${idCalculo}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.erro || 'Falha ao deletar item.');
        const itemParaRemover = document.getElementById(`history-item-${idCalculo}`);
        if (itemParaRemover) {
            itemParaRemover.remove();
        }
    } catch (error) {
        alert(error.message);
    }
}
window.handleDeleteCalculation = handleDeleteCalculation;

/**
 * Busca um resultado específico do histórico e redireciona para a página de resultados.
 */
async function handleViewResult(idCalculo) {
    const token = localStorage.getItem('accessToken');
    if (!token) return;
    try {
        const response = await fetch(`/api/historico/${idCalculo}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.erro || 'Falha ao buscar detalhes.');
        localStorage.setItem('simulationResult', JSON.stringify(result));
        window.location.href = '/resultados';
    } catch (error) {
        alert(error.message);
    }
}
window.handleViewResult = handleViewResult;

/**
 * Copia um resumo do resultado do cálculo para a área de transferência.
 */
function handleCopyCalculation(item) {
    const textToCopy = `Resultado Simulação - EasyInvest\n------------------------------------\nTipo: ${item.tipo_investimento}\nValor Investido: ${item.valor_investido}\nPrazo: ${item.prazo_dias} dias\nTaxa: ${item.taxa_utilizada}\nResultado Líquido: ${item.resultado_liquido}`;
    navigator.clipboard.writeText(textToCopy.trim())
        .then(() => alert("Resultado copiado para a área de transferência!"))
        .catch(err => alert("Não foi possível copiar o resultado."));
}
window.handleCopyCalculation = handleCopyCalculation;

/**
 * Configura todos os eventos de clique da página.
 */
function initializeEventListeners() {
  document.getElementById("sidebar-toggle").addEventListener("click", toggleSidebar);
  document.querySelector('.new-calc-btn').addEventListener('click', () => window.location.href = '/');
  document.querySelector('.logout-btn').addEventListener('click', () => {
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
  });
}

/**
 * Controla a exibição das abas (Histórico, Dashboard, Perfil).
 */
function setActiveTab(tab) {
  document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));
  document.getElementById(tab + "-tab").classList.add("active");
  document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
  document.querySelector(`[data-tab="${tab}"]`).classList.add("active");
}
window.setActiveTab = setActiveTab;

/**
 * Controla o colapso da barra lateral.
 */
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const toggle = document.getElementById("sidebar-toggle");
  sidebar.classList.toggle("collapsed");
  if (sidebar.classList.contains("collapsed")) {
    toggle.innerHTML = '<i data-lucide="chevron-right"></i>';
  } else {
    toggle.innerHTML = '<i data-lucide="chevron-left"></i>';
  }
  lucide.createIcons();
}

/**
 * Habilita ou desabilita a edição de um campo do formulário de perfil.
 */
function toggleEdit(fieldName) {
    const input = document.getElementById(fieldName);
    const button = input.nextElementSibling; 
    if (input.disabled) {
        input.disabled = false;
        input.focus();
        button.innerHTML = '<i data-lucide="save"></i> Salvar';
        button.onclick = () => saveProfileChanges();
    } else {
        input.disabled = true;
        button.innerHTML = '<i data-lucide="edit-2"></i> Editar';
        button.onclick = () => toggleEdit(fieldName);
        loadProfileData(); 
    }
    lucide.createIcons();
}
window.toggleEdit = toggleEdit;

/**
 * Envia as alterações do perfil para a API.
 */
async function saveProfileChanges() {
    const token = localStorage.getItem('accessToken');
    if (!token) { return; }
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const updatedData = { primeiro_nome: firstName, sobrenome: lastName };
    try {
        const response = await fetch('/api/perfil', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(updatedData)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.erro || 'Falha ao atualizar perfil.');
        const successMessage = document.getElementById('success-message');
        successMessage.querySelector('span').textContent = result.mensagem;
        successMessage.style.display = 'flex';
        setTimeout(() => { successMessage.style.display = 'none'; }, 3000);
        ['firstName', 'lastName', 'email'].forEach(id => {
            const input = document.getElementById(id);
            if (input && input.nextElementSibling) {
                const button = input.nextElementSibling;
                input.disabled = true;
                button.innerHTML = '<i data-lucide="edit-2"></i> Editar';
                button.onclick = () => toggleEdit(id);
            }
        });
        loadProfileData();
        lucide.createIcons();
    } catch (error) {
        alert(error.message);
    }
}

/**
 * Mostra ou esconde o formulário de alteração de senha.
 */
function togglePasswordForm() {
    const form = document.getElementById('password-form');
    if (form.style.display === 'none') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
        document.getElementById('currentPassword').value = '';
        document.getElementById('newPassword').value = '';
        document.getElementById('confirmPassword').value = '';
    }
}
window.togglePasswordForm = togglePasswordForm;

/**
 * Envia os dados de alteração de senha para a API.
 */
async function savePassword() {
    const token = localStorage.getItem('accessToken');
    if (!token) return;
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    if (newPassword !== confirmPassword) {
        alert("A nova senha e a confirmação não coincidem.");
        return;
    }
    if (!newPassword || newPassword.length < 6) {
        alert("A nova senha deve ter pelo menos 6 caracteres.");
        return;
    }
    const passwordData = { senha_atual: currentPassword, nova_senha: newPassword };
    try {
        const response = await fetch('/api/alterar-senha', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(passwordData)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.erro || 'Falha ao alterar a senha.');
        alert(result.mensagem);
        togglePasswordForm();
    } catch (error) {
        alert(error.message);
    }
}
window.savePassword = savePassword;