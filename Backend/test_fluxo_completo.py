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

# --- Credenciais de Atualização ---
NEW_FIRST_NAME = "NovoNome"
NEW_LAST_NAME = "NovoSobreNome"
NEW_PASS = "NovaSenha@456"

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
    # ETAPA 1: [CORRIGIDO] TESTE DE FALHA DE LOGIN INICIAL
    # ----------------------------------------------------
    print("Etapa 1: Testando falha de login com credenciais aleatórias...")
    driver.get(BASE_URL + "/login") 
    time.sleep(1.5) # PAUSA 1.5s

    # --- [CORREÇÃO] Clicar em "Entrar" para abrir o modal ---
    print("Clicando no botão 'Entrar' para abrir o modal...")
    enter_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "openModalBtn"))
    )
    enter_btn.click()

    # --- [CORREÇÃO] Esperar o formulário de login ficar visível ---
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "loginForm"))
    )
    print("Modal de login aberto.")
    # --- [FIM DA CORREÇÃO] ---
    
    # 1. Definir credenciais falsas
    FAKE_EMAIL_INICIAL = f"nao_existe_{timestamp}@easy.com"
    FAKE_PASS_INICIAL = "senhaerrada123"
    print(f"Usando e-mail falso: {FAKE_EMAIL_INICIAL}")

    # 2. Preencher o formulário
    driver.find_element(By.ID, "email").send_keys(FAKE_EMAIL_INICIAL)
    time.sleep(1) # Pausa
    driver.find_element(By.ID, "password").send_keys(FAKE_PASS_INICIAL)
    time.sleep(1) # Pausa
    print("Formulário preenchido com e-mail FALSO.")
    
    # 3. Clicar em Login
    login_form = driver.find_element(By.ID, "loginForm")
    login_button = login_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    # 4. Esperar pelo alerta de ERRO
    print("Aguardando alerta de 'credenciais inválidas'...")
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert_text = alert.text
    
    # --- [MODIFICAÇÃO] Pausa para visualizar o alerta ---
    print(f"Alerta visível. Pausando 3s... (Msg: {alert_text})")
    time.sleep(3)
    # --- [FIM DA MODIFICAÇÃO] ---
    
    alert.accept()
    print("Alerta de falha aceito.")
    print("SUCESSO: Falha no login inicial confirmada.")

    # ----------------------------------------------------
    # ETAPA 2: [CORRIGIDO] REGISTRO DE NOVO USUÁRIO
    # ----------------------------------------------------
    print("\nEtapa 2: Registro...")
    
    # --- [CORREÇÃO] O modal já está aberto. Clicamos direto no link de "Criar Conta" ---
    signup_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "signupBtn")))
    print("Modal já aberto, clicando em 'Não possui uma conta? Vamos criar'...")
    signup_link.click()
    # --- [FIM DA CORREÇÃO] ---

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
    # ETAPA 3: LOGIN
    # ----------------------------------------------------
    print("\nEtapa 3: Login...")
    # O modal de login já está visível após o cadastro
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "loginForm")))
    
    email_field_etapa3 = driver.find_element(By.ID, "email")
    email_field_etapa3.clear()
    email_field_etapa3.send_keys(UNIQUE_EMAIL)
    time.sleep(1.5) # PAUSA 1.5s
    
    pass_field_etapa3 = driver.find_element(By.ID, "password")
    pass_field_etapa3.clear()
    pass_field_etapa3.send_keys(USER_PASS)
    time.sleep(1.5) # PAUSA 1.5s
    
    login_form = driver.find_element(By.ID, "loginForm")
    login_button = login_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    print("Login efetuado.")

    # ----------------------------------------------------
    # ETAPA 4: LOOP DE TESTES DE CÁLCULO
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
    # ETAPA 5: NAVEGAÇÃO PERFIL E DASHBOARD
    # ----------------------------------------------------
    print("\nEtapa 5: Verificando Perfil e Dashboard...")
    
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "calculate-btn")))
    print("Na página da calculadora, clicando no ícone de perfil...")
    
    profile_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "profile-link")))
    profile_link.click()
    time.sleep(1.5) # PAUSA 1.5s
    
    print("Na página de perfil, clicando em 'Dashboard'...")
    dashboard_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='dashboard']")))
    dashboard_btn.click()
    time.sleep(1.5) # PAUSA 1.5s

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "dashboard-tab")))
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "lineChart")))
    print("SUCESSO: Dashboard carregado e visível.")
    
    print("Aguardando 3s para visualização final...")
    time.sleep(3) 

    # ----------------------------------------------------
    # ETAPA 6: NOVO CÁLCULO (A PARTIR DO PERFIL)
    # ----------------------------------------------------
    print("\nEtapa 6: Novo Cálculo a partir do Perfil...")
    
    print("Clicando em 'Novo Cálculo' na sidebar (que redireciona para a home)...")
    new_calc_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "new-calc-btn")))
    new_calc_button.click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "calculate-btn")))
    print("Redirecionado para a página da calculadora com sucesso.")
    time.sleep(1.5) # Pausa para ver a página

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

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "valor-liquido")))
    time.sleep(1.5) # PAUSA 1.5s (para ver bem a página de resultados)

    liquido = driver.find_element(By.ID, "valor-liquido").text
    if liquido != "":
        print(f"SUCESSO (Novo Cálculo): Resultados carregados (Líquido: {liquido})")
    else:
        print(f"FALHA (Novo Cálculo): Página de resultados carregada, mas valores vazios.")

    # ----------------------------------------------------
    # ETAPA 7: VERIFICAÇÃO FINAL DO PERFIL (PÓS-NOVOS CÁLCULOS)
    # ----------------------------------------------------
    print("\nEtapa 7: Verificando Histórico e Dashboard novamente...")

    driver.find_element(By.CLASS_NAME, "new-simulation-btn").click()
    print("Retornando para a calculadora...")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "calculate-btn")))
    
    print("Na página da calculadora, clicando no ícone de perfil...")
    profile_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "profile-link")))
    profile_link.click()

    print("Na página de perfil, clicando em 'Histórico'...")
    historico_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='historico']")))
    historico_btn.click()
    
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "history-content")))
    print("SUCESSO: Conteúdo do histórico carregado (com os novos cálculos).")
    print("Aguardando 3s para visualização do histórico...")
    time.sleep(3)

    print("Na página de perfil, clicando em 'Dashboard' novamente...")
    dashboard_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='dashboard']")))
    dashboard_btn.click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "lineChart")))
    print("SUCESSO: Dashboard recarregado e visível.")
    
    print("Aguardando 7s para visualização final do dashboard (ajustado)...")
    time.sleep(7)

    # ----------------------------------------------------
    # ETAPA 8: NAVEGAR PARA EDITAR PERFIL
    # ----------------------------------------------------
    print("\nEtapa 8: Navegando para 'Editar Perfil'...")

    perfil_tab_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='perfil']")))
    perfil_tab_btn.click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "perfil-tab")))
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Editar Perfil']")))
    print("SUCESSO: Aba 'Editar Perfil' carregada.")

    print("Aguardando 2s para visualização da aba de perfil...")
    time.sleep(2)

    # ----------------------------------------------------
    # ETAPA 9: EDITAR PERFIL (NOME E SENHA)
    # ----------------------------------------------------
    print("\nEtapa 9: Editando Nome, Sobrenome e Senha...")
    
    print("Alterando nome e sobrenome...")
    
    edit_first_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='firstName']/following-sibling::button"))
    )
    edit_first_btn.click()
    time.sleep(0.5) # Pausa curta

    edit_last_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='lastName']/following-sibling::button"))
    )
    edit_last_btn.click()
    time.sleep(0.5) # Pausa curta

    first_name_input = driver.find_element(By.ID, "firstName")
    first_name_input.clear()
    first_name_input.send_keys(NEW_FIRST_NAME)
    print(f"Nome preenchido com: {NEW_FIRST_NAME}")
    time.sleep(2.5) # Pausa (ajustada para 2.5s)

    last_name_input = driver.find_element(By.ID, "lastName")
    last_name_input.clear()
    last_name_input.send_keys(NEW_LAST_NAME)
    print(f"Sobrenome preenchido com: {NEW_LAST_NAME}")
    time.sleep(2.5) # Pausa (ajustada para 2.5s)

    edit_first_btn.click()
    
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "success-message"))
    )
    print("SUCESSO: Mensagem de 'perfil atualizado' exibida.")
    print("Aguardando 5s para visualizar a mensagem de sucesso...")
    time.sleep(5) 

    print("Alterando a senha...")
    
    toggle_pass_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Alterar Senha']"))
    )
    toggle_pass_btn.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "password-form"))
    )
    print("Formulário de alteração de senha visível.")
    time.sleep(1) # Pausa

    driver.find_element(By.ID, "currentPassword").send_keys(USER_PASS)
    time.sleep(1) # Pausa
    driver.find_element(By.ID, "newPassword").send_keys(NEW_PASS)
    time.sleep(1) # Pausa
    driver.find_element(By.ID, "confirmPassword").send_keys(NEW_PASS)
    time.sleep(1) # Pausa
    print("Campos de senha preenchidos.")

    save_pass_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@onclick='savePassword()']"))
    )
    save_pass_btn.click()

    print("Aguardando alerta de sucesso na alteração de senha...")
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert_text = alert.text
    
    # --- [MODIFICAÇÃO] Adicionando pausa de 3s no alerta ---
    print(f"Alerta visível. Pausando 3s... (Msg: {alert_text})")
    time.sleep(3)
    # --- [FIM DA MODIFICAÇÃO] ---

    alert.accept()
    print(f"Alerta aceito com mensagem: {alert_text}")

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "password-form"))
    )
    print("SUCESSO: Senha alterada e formulário oculto.")
    print("Aguardando 5s para visualização...")
    time.sleep(5) 

    # ----------------------------------------------------
    # ETAPA 10: LOGOUT
    # ----------------------------------------------------
    print("\nEtapa 10: Efetuando Logout...")
    
    logout_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "logout-btn"))
    )
    logout_btn.click()

    print("Aguardando redirecionamento para a página de login...")
    WebDriverWait(driver, 10).until(
        EC.url_to_be(BASE_URL + "/login")
    )
    print("SUCESSO: Logout efetuado, URL do login confirmada.")
    
    # --- [CORREÇÃO] Esperar pelo botão "Entrar" (visível) em vez do "loginForm" (oculto) ---
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "openModalBtn"))
    )
    print("Página de login carregada (botão 'Entrar' visível).")
    # --- [FIM DA CORREÇÃO] ---
    
    # --- [MODIFICAÇÃO] Aumentando pausa de visualização ---
    print("Aguardando 7s para visualização...")
    time.sleep(7) 
    # --- [FIM DA MODIFICAÇÃO] ---

    # ----------------------------------------------------
    # ETAPA 11: [CORRIGIDO] TESTE DE FALHA DE LOGIN
    # ----------------------------------------------------
    print("\nEtapa 11: Testando falha de login com e-mail incorreto...")
    
    # --- [CORREÇÃO] A página foi recarregada, precisamos reabrir o modal ---
    print("Clicando no botão 'Entrar' para abrir o modal...")
    enter_btn_etapa11 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "openModalBtn"))
    )
    enter_btn_etapa11.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "loginForm"))
    )
    print("Modal de login aberto.")
    # --- [FIM DA CORREÇÃO] ---
    
    FAKE_EMAIL = f"teste_selenium_{timestamp}_fake@easy.com"
    print(f"Usando e-mail falso: {FAKE_EMAIL}")

    driver.find_element(By.ID, "email").send_keys(FAKE_EMAIL)
    time.sleep(1) # Pausa
    driver.find_element(By.ID, "password").send_keys(NEW_PASS)
    time.sleep(1) # Pausa
    print("Formulário preenchido com e-mail FALSO.")

    login_form = driver.find_element(By.ID, "loginForm")
    login_button = login_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    print("Aguardando alerta de falha no login...")
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert_text = alert.text
    alert.accept()
    print(f"Alerta de falha aceito com mensagem: {alert_text}")
    print("SUCESSO: Falha no login com dados incorretos confirmada.")
    time.sleep(3) # Pausa para visualização

    # ----------------------------------------------------
    # ETAPA 12: LOGIN COM NOVAS CREDENCIAIS E VERIFICAÇÃO FINAL
    # ----------------------------------------------------
    print("\nEtapa 12: Testando Login com credenciais CORRETAS...")

    # O modal já está aberto da etapa anterior
    email_field = driver.find_element(By.ID, "email")
    email_field.clear()
    email_field.send_keys(UNIQUE_EMAIL) # O e-mail original/correto
    time.sleep(1) # Pausa
    
    pass_field = driver.find_element(By.ID, "password")
    pass_field.clear()
    pass_field.send_keys(NEW_PASS) # A nova senha correta
    time.sleep(1) # Pausa
    print("Formulário de login preenchido com as credenciais CORRETAS.")

    login_form = driver.find_element(By.ID, "loginForm")
    login_button = login_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    # --- [CORREÇÃO] Esperar pelo ícone do perfil (o que queremos clicar) em vez do 'calculate-btn' ---
    print("Aguardando página da calculadora carregar (esperando pelo ícone do perfil)...")
    profile_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "profile-link"))
    )
    print("SUCESSO: Login com a nova senha efetuado (ícone do perfil está clicável).")
    # --- [FIM DA CORREÇÃO] ---
    
    time.sleep(1.5) # Pausa para visualização

    print("Verificação final: Checando nome e dashboard...")
    
    # --- [CORREÇÃO] Apenas clicamos no elemento que já encontramos ---
    profile_link.click()
    # --- [FIM DA CORREÇÃO] ---

    expected_name = f"{NEW_FIRST_NAME} {NEW_LAST_NAME}"
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.CLASS_NAME, "profile-name"), expected_name)
    )
    print(f"VERIFICAÇÃO CONCLUÍDA: O nome no perfil é '{expected_name}'.")
    time.sleep(1.5)

    print("Navegando para o Dashboard para verificação final...")
    dashboard_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tab='dashboard']")))
    dashboard_btn.click()
    
    # --- [CORREÇÃO] Adicionando pausa de 1s para resolver race condition do JS ---
    print("Aguardando 1s para o JS iniciar o fetch do dashboard...")
    time.sleep(1) 
    # --- [FIM DA CORREÇÃO] ---

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "lineChart")))
    print("SUCESSO: Dashboard carregado após o login final.")
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

