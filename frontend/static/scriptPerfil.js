// Global state
let activeTab = "historico"
let sidebarCollapsed = false
let history = [
  {
    id: 1,
    title: "CDB 115% CDI",
    date: "2024-01-15",
    amount: 50000,
    result: "Positivo",
  },
  {
    id: 2,
    title: "Tesouro Selic 2029",
    date: "2024-01-10",
    amount: 25000,
    result: "Positivo",
  },
]

const profile = {
  firstName: "João",
  lastName: "Silva",
  email: "joao.silva@email.com",
}

let editingField = null
let showPasswordForm = false

// Declare lucide variable
const lucide = window.lucide

const Chart = window.Chart

// Initialize the app
document.addEventListener("DOMContentLoaded", () => {
  if (typeof lucide !== "undefined") {
    lucide.createIcons()
  }
  initializeEventListeners()
  renderHistory()
  setTimeout(initializeCharts, 100) // Added delay to ensure DOM is ready
})

function initializeEventListeners() {
  // Sidebar toggle
  document.getElementById("sidebar-toggle").addEventListener("click", toggleSidebar)

  // Logout button hover
  const logoutBtn = document.querySelector(".logout-btn")
  if (logoutBtn) {
    logoutBtn.addEventListener("mouseenter", function () {
      this.style.background = "#fef2f2"
      this.style.color = "#dc2626"
    })

    logoutBtn.addEventListener("mouseleave", function () {
      this.style.background = "transparent"
      this.style.color = "#374151"
    })
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar")
  const toggle = document.getElementById("sidebar-toggle")

  sidebarCollapsed = !sidebarCollapsed

  if (sidebarCollapsed) {
    sidebar.classList.add("collapsed")
    toggle.innerHTML = '<i data-lucide="chevron-right"></i>'
  } else {
    sidebar.classList.remove("collapsed")
    toggle.innerHTML = '<i data-lucide="chevron-left"></i>'
  }

  if (typeof lucide !== "undefined") {
    lucide.createIcons()
  }
}

function setActiveTab(tab) {
  // Update active tab
  activeTab = tab

  // Hide all tab contents
  document.querySelectorAll(".tab-content").forEach((content) => {
    content.classList.remove("active")
  })

  // Show selected tab content
  const tabContent = document.getElementById(tab + "-tab")
  if (tabContent) {
    tabContent.classList.add("active")
  }

  // Update navigation buttons
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.remove("active")
  })

  const activeBtn = document.querySelector(`[data-tab="${tab}"]`)
  if (activeBtn) {
    activeBtn.classList.add("active")
  }

  // Re-render charts if dashboard is selected
  if (tab === "dashboard") {
    setTimeout(initializeCharts, 100)
  }
}

window.setActiveTab = setActiveTab

function renderHistory() {
  const emptyState = document.getElementById("empty-state")
  const historyContent = document.getElementById("history-content")
  const historyList = document.getElementById("history-list")

  if (history.length === 0) {
    emptyState.style.display = "flex"
    historyContent.style.display = "none"
  } else {
    emptyState.style.display = "none"
    historyContent.style.display = "block"

    historyList.innerHTML = history
      .map(
        (item) => `
            <div class="history-item">
                <div class="history-item-content">
                    <div class="history-item-info">
                        <p>Resultado para:</p>
                        <p>${item.title}</p>
                        <p>${new Date(item.date).toLocaleDateString("pt-BR")}</p>
                    </div>
                    <div class="history-item-actions">
                        <button class="btn btn-outline btn-sm" onclick="copyCalculationResults(${item.id})">
                            <i data-lucide="copy"></i>
                            Copiar
                        </button>
                        <button class="btn btn-outline btn-sm">
                            <i data-lucide="eye"></i>
                            Ver resultados
                        </button>
                        <button class="btn btn-outline btn-sm" onclick="deleteHistoryItem(${item.id})" style="color: #dc2626;">
                            <i data-lucide="trash-2"></i>
                        </button>
                    </div>
                </div>
            </div>
        `,
      )
      .join("")

    if (typeof lucide !== "undefined") {
      lucide.createIcons()
    }
  }
}

function deleteHistoryItem(id) {
  history = history.filter((item) => item.id !== id)
  renderHistory()
}

window.deleteHistoryItem = deleteHistoryItem

function copyCalculationResults(id) {
  const item = history.find((h) => h.id === id)
  const template = `Valor investido (R$): R$ ${item.amount.toLocaleString()} 
Prazo do investimento (dias): 180 dias 

Taxas utilizadas: ${item.title} 

Rendimento bruto: R$ 41.500 

Alíquota de IR: 15% 

Valor de IR: R$ 975 

Valor Líquido: R$ 40.525 

Valor líquido do título público: R$ 39.800 

Diferença em R$: +R$ 725 
 
Diferença em %: +1.82%`
 
  navigator.clipboard.writeText(template)
  showMessage("copied-message", "Resultados copiados!")
}

window.copyCalculationResults = copyCalculationResults

function toggleEdit(field) {
  const input = document.getElementById(field)
  const button = input.nextElementSibling

  if (editingField === field) {
    // Save
    profile[field] = input.value
    input.disabled = true
    button.textContent = "Editar"
    editingField = null
    showSuccessMessage("Perfil atualizado com sucesso!")
  } else {
    // Edit
    input.disabled = false
    input.focus()
    button.textContent = "Salvar"
    editingField = field
  }
}

window.toggleEdit = toggleEdit

function togglePasswordForm() {
  const form = document.getElementById("password-form")
  showPasswordForm = !showPasswordForm

  if (showPasswordForm) {
    form.style.display = "block"
  } else {
    form.style.display = "none"
    // Clear form
    document.getElementById("currentPassword").value = ""
    document.getElementById("newPassword").value = ""
    document.getElementById("confirmPassword").value = ""
  }
}

window.togglePasswordForm = togglePasswordForm

function savePassword() {
  const currentPassword = document.getElementById("currentPassword").value
  const newPassword = document.getElementById("newPassword").value
  const confirmPassword = document.getElementById("confirmPassword").value

  if (newPassword !== confirmPassword) {
    alert("As senhas não coincidem!")
    return
  }

  togglePasswordForm()
  showSuccessMessage("Senha atualizada com sucesso!")
}

window.savePassword = savePassword

function showMessage(elementId, message) {
  const element = document.getElementById(elementId)
  if (element) {
    element.textContent = message
    setTimeout(() => {
      element.textContent = ""
    }, 3000)
  }
}

function showSuccessMessage(message) {
  const alert = document.getElementById("success-message")
  if (alert) {
    const span = alert.querySelector("span")
    if (span) {
      span.textContent = message
    }
    alert.style.display = "flex"
    setTimeout(() => {
      alert.style.display = "none"
    }, 3000)
  }
}

function initializeCharts() {
  if (typeof Chart === "undefined") {
    console.error("Chart.js não foi carregado")
    return
  }

  // Chart data
  const chartData = [
    { name: "Jan", investido: 10000, rendimento: 10500 },
    { name: "Fev", investido: 15000, rendimento: 16200 },
    { name: "Mar", investido: 20000, rendimento: 22100 },
    { name: "Abr", investido: 25000, rendimento: 28300 },
    { name: "Mai", investido: 30000, rendimento: 34800 },
    { name: "Jun", investido: 35000, rendimento: 41500 },
  ]

  const pieData = [
    { name: "CDB", value: 45, color: "#363071" },
    { name: "Tesouro Direto", value: 30, color: "#9E9EA3" },
    { name: "LCI/LCA", value: 15, color: "#EFEDFF" },
    { name: "Fundos", value: 10, color: "#B8B5FF" },
  ]

  // Line Chart
  const lineCtx = document.getElementById("lineChart")
  if (lineCtx) {
    new Chart(lineCtx, {
      type: "line",
      data: {
        labels: chartData.map((d) => d.name),
        datasets: [
          {
            label: "Investido",
            data: chartData.map((d) => d.investido),
            borderColor: "#363071",
            backgroundColor: "rgba(54, 48, 113, 0.1)",
            tension: 0.4,
          },
          {
            label: "Rendimento",
            data: chartData.map((d) => d.rendimento),
            borderColor: "#9E9EA3",
            backgroundColor: "rgba(158, 158, 163, 0.1)",
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => "R$ " + value.toLocaleString(),
            },
          },
        },
      },
    })
  }

  // Bar Chart
  const barCtx = document.getElementById("barChart")
  if (barCtx) {
    new Chart(barCtx, {
      type: "bar",
      data: {
        labels: chartData.map((d) => d.name),
        datasets: [
          {
            label: "Investido",
            data: chartData.map((d) => d.investido),
            backgroundColor: "#363071",
          },
          {
            label: "Rendimento",
            data: chartData.map((d) => d.rendimento),
            backgroundColor: "#EFEDFF",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => "R$ " + value.toLocaleString(),
            },
          },
        },
      },
    })
  }

  // Pie Chart
  const pieCtx = document.getElementById("pieChart")
  if (pieCtx) {
    new Chart(pieCtx, {
      type: "pie",
      data: {
        labels: pieData.map((d) => d.name),
        datasets: [
          {
            data: pieData.map((d) => d.value),
            backgroundColor: pieData.map((d) => d.color),
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
          },
          tooltip: {
            callbacks: {
              label: (context) => context.label + ": " + context.parsed + "%",
            },
          },
        },
      },
    })
  }
}
