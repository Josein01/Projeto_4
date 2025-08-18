// Estado da aplicação
let currentMode = "login" // 'login', 'recovery', 'signup'

// Elementos do DOM
const modal = document.getElementById("modal")
const openModalBtn = document.getElementById("openModalBtn")
const backBtn = document.getElementById("backBtn")
const modalTitle = document.getElementById("modalTitle")

// Formulários
const loginForm = document.getElementById("loginForm")
const recoveryForm = document.getElementById("recoveryForm")
const signupForm = document.getElementById("signupForm")

// Botões de navegação
const forgotPasswordBtn = document.getElementById("forgotPasswordBtn")
const signupBtn = document.getElementById("signupBtn")

// Event Listeners
openModalBtn.addEventListener("click", openModal)
backBtn.addEventListener("click", goBackToLogin)
forgotPasswordBtn.addEventListener("click", goToRecovery)
signupBtn.addEventListener("click", goToSignup)

// Fechar modal clicando fora
modal.addEventListener("click", (e) => {
  if (e.target === modal) {
    closeModal()
  }
})

// Handlers dos formulários
loginForm.addEventListener("submit", handleLogin)
recoveryForm.addEventListener("submit", handleRecovery)
signupForm.addEventListener("submit", handleSignup)

// Funções principais
function openModal() {
  modal.classList.add("show")
  currentMode = "login"
  updateModalContent()
}

function closeModal() {
  modal.classList.remove("show")
  resetForms()
}

function goToRecovery() {
  currentMode = "recovery"
  updateModalContent()
}

function goToSignup() {
  currentMode = "signup"
  updateModalContent()
}

function goBackToLogin() {
  currentMode = "login"
  updateModalContent()
}

function updateModalContent() {
  // Esconder todos os formulários
  loginForm.style.display = "none"
  recoveryForm.style.display = "none"
  signupForm.style.display = "none"

  // Mostrar/esconder botão de voltar
  if (currentMode === "login") {
    backBtn.style.display = "none"
    modalTitle.textContent = "Fazer Login"
    loginForm.style.display = "flex"
  } else if (currentMode === "recovery") {
    backBtn.style.display = "block"
    modalTitle.textContent = "Recuperar Conta"
    recoveryForm.style.display = "flex"
  } else if (currentMode === "signup") {
    backBtn.style.display = "block"
    modalTitle.textContent = "Criar Conta"
    signupForm.style.display = "flex"
  }
}

function resetForms() {
  loginForm.reset()
  recoveryForm.reset()
  signupForm.reset()
  currentMode = "login"
}

// Handlers dos formulários
function handleLogin(e) {
  e.preventDefault()
  const email = document.getElementById("email").value
  const password = document.getElementById("password").value

  console.log("Login:", { email, password })
  // Aqui você adicionaria a lógica de login
  alert("Login realizado com sucesso!")
}

function handleRecovery(e) {
  e.preventDefault()
  const recoveryEmail = document.getElementById("recoveryEmail").value

  console.log("Recuperação:", { recoveryEmail })
  // Aqui você adicionaria a lógica de recuperação
  alert("Email de recuperação enviado!")
}

function handleSignup(e) {
  e.preventDefault()
  const firstName = document.getElementById("firstName").value
  const lastName = document.getElementById("lastName").value
  const email = document.getElementById("signupEmail").value
  const password = document.getElementById("signupPassword").value
  const confirmPassword = document.getElementById("confirmPassword").value

  if (password !== confirmPassword) {
    alert("As senhas não coincidem!")
    return
  }

  console.log("Cadastro:", { firstName, lastName, email, password })
  // Aqui você adicionaria a lógica de cadastro
  alert("Conta criada com sucesso!")
}
