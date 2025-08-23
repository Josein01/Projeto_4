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
modal.addEventListener("click", (e) => {
  if (e.target === modal) closeModal()
})

// Handlers dos formulários que agora chamam a API
loginForm.addEventListener("submit", handleLogin)
recoveryForm.addEventListener("submit", handleRecovery)
signupForm.addEventListener("submit", handleSignup)

// Funções de controle do Modal
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
  loginForm.style.display = "none"
  recoveryForm.style.display = "none"
  signupForm.style.display = "none"
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
  loginForm.reset();
  recoveryForm.reset();
  signupForm.reset();
  currentMode = "login";
}

// --- LÓGICA DE INTEGRAÇÃO COM A API E REDIRECIONAMENTOS ---

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const loginData = { email: email, senha: password };

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.erro || 'Falha no login.');
    
    // Salva o token de acesso no navegador
    localStorage.setItem('accessToken', result.access_token);
    
    // **REDIRECIONAMENTO PARA A CALCULADORA (index.html)**
    window.location.href = '/'; 
  } catch (error) {
    alert(error.message);
  }
}

async function handleRecovery(e) {
  e.preventDefault();
  const recoveryEmail = document.getElementById("recoveryEmail").value;
  
  try {
    const response = await fetch('/api/recuperar-senha', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: recoveryEmail })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.erro || 'Falha ao enviar e-mail.');

    alert(result.mensagem);

    // **REDIRECIONAMENTO DE VOLTA PARA A TELA DE LOGIN**
    goBackToLogin();
  } catch (error) {
    alert(error.message);
  }
}

async function handleSignup(e) {
  e.preventDefault();
  const firstName = document.getElementById("firstName").value;
  const lastName = document.getElementById("lastName").value;
  const email = document.getElementById("signupEmail").value;
  const password = document.getElementById("signupPassword").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  if (password !== confirmPassword) {
    alert("As senhas não coincidem!");
    return;
  }

  const signupData = { 
    primeiro_nome: firstName, 
    sobrenome: lastName, 
    email: email, 
    senha: password 
  };
  
  try {
    const response = await fetch('/api/registrar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(signupData)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.erro || 'Falha ao criar conta.');

    alert(result.mensagem);

    // **REDIRECIONAMENTO DE VOLTA PARA A TELA DE LOGIN**
    goBackToLogin(); 
  } catch (error) {
    alert(error.message);
  }
}