import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuração (MODIFICADA PARA CHROMIUM) ---
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/chromium-browser" 
chrome_options.add_experimental_option("detach", True) 
service = Service(executable_path="/usr/bin/chromedriver") 
driver = webdriver.Chrome(service=service, options=chrome_options)
# Aumentamos o wait implícito para 10s para dar mais folga
driver.implicitly_wait(10) 

BASE_URL = "http://127.0.0.1:5000"

# --- Dados de Teste ---
timestamp = int(time.time())
UNIQUE_EMAIL = f"teste_selenium_{timestamp}@easy.com"
USER_PASS = "SenhaForte@123"

# --- [NOVO] Credenciais de Atualização ---
# --- [MODIFICAÇÃO] Nomes encurtados para caber no banco de dados ---
NEW_FIRST_NAME = "NovoNome"
NEW_LAST_NAME = "NovoSobreNome"
NEW_PASS = "NovaSenha@456"
# --- [FIM NOVO] ---

# --- Cenários de Teste ---
scenarios = [
    {
        "name": "CDB/RDB",
        "button_selector": "//button[@data-option='CDB/RDB']",
        "data": {
            "investment-value": "1000",
            "time-period": "365",
            "cdi-percentage": "100"
        }
    },
    {
        "name": "LCI/LCA",
        "button_selector": "//button[@data-option='LCI/LCA']",
        "data": {
            "investment-value": "5000",
            "time-period": "720",
            "cdi-percentage": "120"
        }
    },
    {
        "name": "Tesouro Direito",
        "button_selector": "//button[@data-option='Tesouro Direito']",
        "data": {
            "investment-value": "2000",
            "time-period": "1080"
        }
    }
]

print(f"Iniciando teste E2E com o usuário: {UNIQUE_EMAIL}")

try:
    # ----------------------------------------------------
    # ETAPA 1: REGISTRO DE NOVO USUÁRIO
    # ----------------------------------------------------
    print("Etapa 1: Registro...")
    driver.get(BASE_URL + "/login") 
    time.sleep(1.5) # PAUSA 1.5s
    driver.find_element(By.ID, "openModalBtn").click()

    signup_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "signupBtn")))
    time.sleep(1.5) # PAUSA 1.5s
    signup_link.click()

    print("Preenchendo formulário de cadastro...")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "signupForm")))
    driver.find_element(By.ID, "firstName").send_keys("Usuario")
    time.sleep(1.5) # PAUSA 1.5s
    driver.find_element(By.ID, "lastName").send_keys("Teste")
    time.sleep(1.5) # PAUSA 1.5s
    driver.find_element(By.ID, "signupEmail").send_keys(UNIQUE_EMAIL)
    time.sleep(1.5) # PAUSA 1.5s
    driver.find_element(By.ID, "signupPassword").send_keys(USER_PASS)
    time.sleep(1.5) # PAUSA 1.5s
    driver.find_element(By.ID, "confirmPassword").send_keys(USER_PASS)
    time.sleep(1.5) # PAUSA 1.5s
    
    signup_form = driver.find_element(By.ID, "signupForm")
    signup_form.find_element(By.TAG_NAME, "button").click()

    print("Aguardando alerta de sucesso no cadastro...")
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    time.sleep(1.5) # PAUSA 1.5s (para o alerta ficar visível)
    alert.accept()
    print("Alerta aceito.")
    time.sleep(1.5) # PAUSA 1.5s
    
    print("Registro concluído. Aguardando formulário de login...")

    # ----------------------------------------------------
    # ETAPA 2: LOGIN
    # ----------------------------------------------------
    print("Etapa 2: Login...")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "loginForm")))
    driver.find_element(By.ID, "email").send_keys(UNIQUE_EMAIL)
    time.sleep(1.5) # PAUSA 1.5s
    driver.find_element(By.ID, "password").send_keys(USER_PASS)
    time.sleep(1.5) # PAUSA 1.5s
    
    login_form = driver.find_element(By.ID, "loginForm")
    login_button = login_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    print("Login efetuado.")

    # ----------------------------------------------------
    # ETAPA 3: LOOP DE TESTES DE CÁLCULO
    # ----------------------------------------------------
    
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "calculate-btn")))
    time.sleep(1.5) # PAUSA 1.5s (para ver a página da calculadora)
    
    for scenario in scenarios:
        print(f"\n--- Iniciando Cenário: {scenario['name']} ---")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "calculate-btn")))

        driver.find_element(By.XPATH, scenario["button_selector"]).click()
        print(f"Selecionado tipo: {scenario['name']}")
        time.sleep(1.5) # PAUSA 1.5s

        for field_id, value in scenario["data"].items():
            element = driver.find_element(By.ID, field_id)
            element.clear()
            time.sleep(1.5) # PAUSA 1.5s
            element.send_keys(value)
            print(f"Preenchido {field_id} com {value}")
            time.sleep(1.5) # PAUSA 1.5s
        
        time.sleep(1.5) # PAUSA 1.5s (antes de clicar em calcular)
        driver.find_element(By.ID, "calculate-btn").click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "valor-liquido")))
        
        # --- [MODIFICAÇÃO] Pausas personalizadas por cenário ---
        if scenario['name'] == "CDB/RDB":
            print("Pausando 10s para ver resultados (CDB/RDB)...")
            time.sleep(10)
        elif scenario['name'] == "LCI/LCA":
            print("Pausando 5s para ver resultados (LCI/LCA)...")
            time.sleep(5)
        elif scenario['name'] == "Tesouro Direito":
            print("Pausando 3s para ver resultados (Tesouro Direito)...")
            time.sleep(3)
        else:
            time.sleep(1.5) # Pausa padrão
        # --- [FIM DA MODIFICAÇÃO] ---

        investido = driver.find_element(By.ID, "valor-investido").text
        liquido = driver.find_element(By.ID, "valor-liquido").text

        if investido != "" and liquido != "":
            print(f"SUCESSO ({scenario['name']}): Resultados carregados (Líquido: {liquido})")
        else:
            print(f"FALHA ({scenario['name']}): Página de resultados carregada, mas valores vazios.")
        
        driver.find_element(By.CLASS_NAME, "new-simulation-btn").click()
        print("Retornando para a calculadora...")
        time.sleep(1.5) # PAUSA 1.5s (para ver a volta)

    print("\n--- SIMULAÇÕES CONCLUÍDAS ---")

    # ----------------------------------------------------
    # ETAPA 4: NAVEGAÇÃO PERFIL E DASHBOARD
    # ----------------------------------------------------
    print("\nEtapa 4: Verificando Perfil e Dashboard...")
    
    # Espera estar de volta na página da calculadora antes de prosseguir
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "calculate-btn")))
    print("Na página da calculadora, clicando no ícone de perfil...")
    
    # Clica no ícone de Perfil (do index.html)
    profile_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "profile-link")))
    profile_link.click()
    time.sleep(1.5) # PAUSA 1.5s
    
    # Clica no botão Dashboard (do Perfil.html)
    print("Na página de perfil, clicando em 'Dashboard'...")
    # Usamos o seletor de atributo que é único para o botão do dashboard
    dashboard_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='dashboard']")))
    dashboard_btn.click()
    time.sleep(1.5) # PAUSA 1.5s

    # Aguarda o conteúdo do dashboard (o gráfico de linha) ficar visível
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "dashboard-tab")))
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "lineChart")))
    print("SUCESSO: Dashboard carregado e visível.")
    
    # Espera final para visualização
    print("Aguardando 3s para visualização final...")
    time.sleep(3) 

    # ----------------------------------------------------
    # ETAPA 5: NOVO CÁLCULO (A PARTIR DO PERFIL)
    # ----------------------------------------------------
    print("\nEtapa 5: Novo Cálculo a partir do Perfil...")
    
    # --- [MODIFICAÇÃO] Corrigindo o fluxo de "Novo Cálculo" ---
    # O scriptPerfil.js mostra que o botão .new-calc-btn agora redireciona para a home
    print("Clicando em 'Novo Cálculo' na sidebar (que redireciona para a home)...")
    new_calc_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "new-calc-btn")))
    new_calc_button.click()

    # 2. Esperar ser redirecionado para a página da calculadora
    # Fazemos isso esperando o botão "calculate-btn" ficar visível
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "calculate-btn")))
    print("Redirecionado para a página da calculadora com sucesso.")
    time.sleep(1.5) # Pausa para ver a página

    # 3. Executar um novo cenário (LCI/LCA com valores diferentes)
    scenario_etapa_5 = {
        "name": "LCI/LCA (Teste 2)",
        "button_selector": "//button[@data-option='LCI/LCA']",
        "data": {
            "investment-value": "8000",
            "time-period": "1000",
            "cdi-percentage": "115"
        }
    }
    print(f"\n--- Executando novo cenário: {scenario_etapa_5['name']} ---")

    driver.find_element(By.XPATH, scenario_etapa_5["button_selector"]).click()
    print(f"Selecionado tipo: {scenario_etapa_5['name']}")
    time.sleep(1.5) # PAUSA 1.5s

    for field_id, value in scenario_etapa_5["data"].items():
        element = driver.find_element(By.ID, field_id)
        element.clear()
        time.sleep(1.5) # PAUSA 1.5s
        element.send_keys(value)
        print(f"Preenchido {field_id} com {value}")
        time.sleep(1.5) # PAUSA 1.5s
    
    time.sleep(1.5) # PAUSA 1.5s (antes de clicar em calcular)
    driver.find_element(By.ID, "calculate-btn").click()

    # 4. Verificar resultados
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "valor-liquido")))
    time.sleep(1.5) # PAUSA 1.5s (para ver bem a página de resultados)

    liquido = driver.find_element(By.ID, "valor-liquido").text
    if liquido != "":
        print(f"SUCESSO (Novo Cálculo): Resultados carregados (Líquido: {liquido})")
    else:
        print(f"FALHA (Novo Cálculo): Página de resultados carregada, mas valores vazios.")

    # ----------------------------------------------------
    # ETAPA 6: VERIFICAÇÃO FINAL DO PERFIL (PÓS-NOVOS CÁLCULOS)
    # ----------------------------------------------------
    print("\nEtapa 6: Verificando Histórico e Dashboard novamente...")

    # 1. Voltar para a página da calculadora (a partir da pág. de Resultados)
    driver.find_element(By.CLASS_NAME, "new-simulation-btn").click()
    print("Retornando para a calculadora...")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "calculate-btn")))
    
    # 2. Clicar no ícone de Perfil (do index.html)
    print("Na página da calculadora, clicando no ícone de perfil...")
    profile_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "profile-link")))
    profile_link.click()

    # 3. Esperar a página de perfil carregar e clicar em 'Histórico'
    # (Embora seja a aba padrão, clicamos para garantir a ação)
    print("Na página de perfil, clicando em 'Histórico'...")
    historico_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='historico']")))
    historico_btn.click()
    
    # 4. Esperar o conteúdo do histórico (NÃO o 'empty-state')
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "history-content")))
    print("SUCESSO: Conteúdo do histórico carregado (com os novos cálculos).")
    print("Aguardando 3s para visualização do histórico...")
    time.sleep(3)

    # 5. Clicar no botão Dashboard (do Perfil.html)
    print("Na página de perfil, clicando em 'Dashboard' novamente...")
    dashboard_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='dashboard']")))
    dashboard_btn.click()

    # 6. Aguarda o conteúdo do dashboard (o gráfico de linha) ficar visível
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "lineChart")))
    print("SUCESSO: Dashboard recarregado e visível.")
    
    # 7. Espera final
    # --- [MODIFICAÇÃO] Pausa aumentada ---
    print("Aguardando 7s para visualização final do dashboard (ajustado)...")
    time.sleep(7)
    # --- [FIM DA MODIFICAÇÃO] ---

    # ----------------------------------------------------
    # ETAPA 7: NAVEGAR PARA EDITAR PERFIL
    # ----------------------------------------------------
    print("\nEtapa 7: Navegando para 'Editar Perfil'...")

    # 1. Clicar no botão "Editar Perfil" (data-tab='perfil')
    # Já estamos na página de perfil, apenas trocamos de aba
    perfil_tab_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='perfil']")))
    perfil_tab_btn.click()

    # 2. Aguardar o conteúdo da aba de perfil ficar visível
    # Vamos esperar pelo header "Editar Perfil" (h2)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "perfil-tab")))
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Editar Perfil']")))
    print("SUCESSO: Aba 'Editar Perfil' carregada.")

    # Pausa para visualização
    print("Aguardando 2s para visualização da aba de perfil...")
    time.sleep(2)

    # ----------------------------------------------------
    # ETAPA 8: EDITAR PERFIL (NOME E SENHA)
    # ----------------------------------------------------
    print("\nEtapa 8: Editando Nome, Sobrenome e Senha...")
    
    # --- Alterar Nome e Sobrenome ---
    print("Alterando nome e sobrenome...")
    
    # 1. Clicar em "Editar" Nome
    edit_first_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='firstName']/following-sibling::button"))
    )
    edit_first_btn.click()
    time.sleep(0.5) # Pausa curta

    # 2. Clicar em "Editar" Sobrenome
    edit_last_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='lastName']/following-sibling::button"))
    )
    edit_last_btn.click()
    time.sleep(0.5) # Pausa curta

    # 3. Preencher novos valores
    first_name_input = driver.find_element(By.ID, "firstName")
    first_name_input.clear()
    first_name_input.send_keys(NEW_FIRST_NAME)
    print(f"Nome preenchido com: {NEW_FIRST_NAME}")
    # --- [MODIFICAÇÃO] Pausa aumentada ---
    time.sleep(2.5) # Pausa (ajustada para 2.5s)
    # --- [FIM DA MODIFICAÇÃO] ---

    last_name_input = driver.find_element(By.ID, "lastName")
    last_name_input.clear()
    last_name_input.send_keys(NEW_LAST_NAME)
    print(f"Sobrenome preenchido com: {NEW_LAST_NAME}")
    # --- [MODIFICAÇÃO] Pausa aumentada ---
    time.sleep(2.5) # Pausa (ajustada para 2.5s)
    # --- [FIM DA MODIFICAÇÃO] ---

    # 4. Clicar em "Salvar" (pode ser qualquer um dos botões, usamos o do nome)
    # O botão de "Editar" agora é o de "Salvar"
    edit_first_btn.click()
    
    # 5. Esperar pela mensagem de sucesso (conforme scriptPerfil.js)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "success-message"))
    )
    print("SUCESSO: Mensagem de 'perfil atualizado' exibida.")
    # --- [MODIFICAÇÃO] Pausa aumentada ---
    # A mensagem desaparece em 3s (via JS), pausamos por 5s (ajustado).
    print("Aguardando 5s para visualizar a mensagem de sucesso...")
    time.sleep(5) 
    # --- [FIM DA MODIFICAÇÃO] ---

    # --- Alterar Senha ---
    print("Alterando a senha...")
    
    # 1. Clicar em "Alterar Senha" para abrir o formulário
    toggle_pass_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Alterar Senha']"))
    )
    toggle_pass_btn.click()

    # 2. Esperar formulário ficar visível
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "password-form"))
    )
    print("Formulário de alteração de senha visível.")
    time.sleep(1) # Pausa

    # 3. Preencher senhas
    driver.find_element(By.ID, "currentPassword").send_keys(USER_PASS)
    time.sleep(1) # Pausa
    driver.find_element(By.ID, "newPassword").send_keys(NEW_PASS)
    time.sleep(1) # Pausa
    driver.find_element(By.ID, "confirmPassword").send_keys(NEW_PASS)
    time.sleep(1) # Pausa
    print("Campos de senha preenchidos.")

    # 4. Clicar em "Salvar Senha"
    save_pass_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@onclick='savePassword()']"))
    )
    save_pass_btn.click()

    # 5. Esperar pelo alerta de sucesso (conforme scriptPerfil.js)
    print("Aguardando alerta de sucesso na alteração de senha...")
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert_text = alert.text
    alert.accept()
    print(f"Alerta aceito com mensagem: {alert_text}")

    # 6. Esperar o formulário de senha desaparecer
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "password-form"))
    )
    print("SUCESSO: Senha alterada e formulário oculto.")
    # --- [MODIFICAÇÃO] Pausa aumentada ---
    time.sleep(3) # Era 2s
    # --- [FIM DA MODIFICAÇÃO] ---

    # ----------------------------------------------------
    # ETAPA 9: LOGOUT
    # ----------------------------------------------------
    print("\nEtapa 9: Efetuando Logout...")
    
    # 1. Clicar no botão de Logout (conforme scriptPerfil.js)
    logout_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "logout-btn"))
    )
    logout_btn.click()

    # 2. Esperar ser redirecionado para a página de login
    # --- [MODIFICAÇÃO] Trocando espera de Elemento por espera de URL ---
    # Isso é mais estável após um redirecionamento, evitando o erro 'Message: '
    print("Aguardando redirecionamento para a página de login...")
    WebDriverWait(driver, 10).until(
        EC.url_to_be(BASE_URL + "/login")
    )
    print("SUCESSO: Logout efetuado, URL do login confirmada.")
    
    # 3. [NOVO] Adicionamos uma verificação extra para garantir que o formulário está visível
    # antes de prosseguir para a Etapa 10, garantindo que a página carregou.
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "loginForm"))
    )
    print("Formulário de login visível.")
    # --- [FIM DA MODIFICAÇÃO] ---
    # --- [MODIFICAÇÃO] Pausa aumentada ---
    time.sleep(3) # Era 2s
    # --- [FIM DA MODIFICAÇÃO] ---

    # ----------------------------------------------------
    # ETAPA 10: LOGIN COM NOVAS CREDENCIAIS E VERIFICAÇÃO
    # ----------------------------------------------------
    print("\nEtapa 10: Testando Login com novas credenciais...")

    # 1. Preencher e-mail (o mesmo) e a NOVA senha
    driver.find_element(By.ID, "email").send_keys(UNIQUE_EMAIL)
    time.sleep(1) # Pausa
    driver.find_element(By.ID, "password").send_keys(NEW_PASS)
    time.sleep(1) # Pausa
    print("Formulário de login preenchido com a NOVA senha.")

    # 2. Clicar em Login
    login_form = driver.find_element(By.ID, "loginForm")
    login_button = login_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    # 3. Esperar carregar a página da calculadora (confirma o login)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "calculate-btn"))
    )
    print("SUCESSO: Login com a nova senha efetuado.")
    time.sleep(1.5)

    # 4. VERIFICAÇÃO FINAL: Checar se o nome foi alterado
    print("Verificação final: Checando se o nome foi alterado no perfil...")
    
    # 4a. Clicar no ícone de Perfil
    profile_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "profile-link"))
    )
    profile_link.click()

    # 4b. Esperar o nome do perfil carregar E ter o texto esperado
    expected_name = f"{NEW_FIRST_NAME} {NEW_LAST_NAME}"
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.CLASS_NAME, "profile-name"), expected_name)
    )
    print(f"VERIFICAÇÃO CONCLUÍDA: O nome no perfil é '{expected_name}'.")
    time.sleep(3) # Pausa final para visualização


    print("\n--- TESTE DE FLUXO COMPLETO CONCLUÍDO (COM SUCESSO) ---")

except Exception as e:
    print(f"\n--- O TESTE FALHOU ---")
    print(f"Erro: {e}")
    print("Verifique os IDs, o fluxo ou se o servidor está rodando.")

finally:
    print("Fim do teste.")
    # A opção 'detach' manterá o navegador aberto.
    # driver.quit()