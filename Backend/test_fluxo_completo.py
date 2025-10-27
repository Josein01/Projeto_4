import time # (O import já estava lá, mas só para garantir)
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
driver.implicitly_wait(5) 

BASE_URL = "http://127.0.0.1:5000"

# --- Dados de Teste ---
timestamp = int(time.time())
UNIQUE_EMAIL = f"teste_selenium_{timestamp}@easy.com"
USER_PASS = "SenhaForte@123"

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
    time.sleep(1) # PAUSA 1s
    driver.find_element(By.ID, "openModalBtn").click()

    signup_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "signupBtn")))
    time.sleep(1) # PAUSA 1s
    signup_link.click()

    print("Preenchendo formulário de cadastro...")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "signupForm")))
    driver.find_element(By.ID, "firstName").send_keys("Usuario")
    time.sleep(0.5) # PAUSA 0.5s
    driver.find_element(By.ID, "lastName").send_keys("Teste")
    time.sleep(0.5) # PAUSA 0.5s
    driver.find_element(By.ID, "signupEmail").send_keys(UNIQUE_EMAIL)
    time.sleep(0.5) # PAUSA 0.5s
    driver.find_element(By.ID, "signupPassword").send_keys(USER_PASS)
    time.sleep(0.5) # PAUSA 0.5s
    driver.find_element(By.ID, "confirmPassword").send_keys(USER_PASS)
    time.sleep(1) # PAUSA 1s
    
    signup_form = driver.find_element(By.ID, "signupForm")
    signup_form.find_element(By.TAG_NAME, "button").click()

    print("Aguardando alerta de sucesso no cadastro...")
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    time.sleep(1) # PAUSA 1s (para o alerta ficar visível)
    alert.accept()
    print("Alerta aceito.")
    time.sleep(1) # PAUSA 1s
    
    print("Registro concluído. Aguardando formulário de login...")

    # ----------------------------------------------------
    # ETAPA 2: LOGIN
    # ----------------------------------------------------
    print("Etapa 2: Login...")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "loginForm")))
    driver.find_element(By.ID, "email").send_keys(UNIQUE_EMAIL)
    time.sleep(0.5) # PAUSA 0.5s
    driver.find_element(By.ID, "password").send_keys(USER_PASS)
    time.sleep(1) # PAUSA 1s
    
    login_form = driver.find_element(By.ID, "loginForm")
    login_button = login_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    print("Login efetuado.")

    # ----------------------------------------------------
    # ETAPA 3: LOOP DE TESTES DE CÁLCULO
    # ----------------------------------------------------
    
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "calculate-btn")))
    time.sleep(1) # PAUSA 1s (para ver a página da calculadora)
    
    for scenario in scenarios:
        print(f"\n--- Iniciando Cenário: {scenario['name']} ---")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "calculate-btn")))

        driver.find_element(By.XPATH, scenario["button_selector"]).click()
        print(f"Selecionado tipo: {scenario['name']}")
        time.sleep(1) # PAUSA 1s

        for field_id, value in scenario["data"].items():
            element = driver.find_element(By.ID, field_id)
            element.clear()
            time.sleep(0.5) # PAUSA 0.5s
            element.send_keys(value)
            print(f"Preenchido {field_id} com {value}")
            time.sleep(0.5) # PAUSA 0.5s
        
        time.sleep(1) # PAUSA 1s (antes de clicar em calcular)
        driver.find_element(By.ID, "calculate-btn").click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "valor-liquido")))
        time.sleep(2) # PAUSA 2s (para ver bem a página de resultados)

        investido = driver.find_element(By.ID, "valor-investido").text
        liquido = driver.find_element(By.ID, "valor-liquido").text

        if investido != "" and liquido != "":
            print(f"SUCESSO ({scenario['name']}): Resultados carregados (Líquido: {liquido})")
        else:
            print(f"FALHA ({scenario['name']}): Página de resultados carregada, mas valores vazios.")
        
        driver.find_element(By.CLASS_NAME, "new-simulation-btn").click()
        print("Retornando para a calculadora...")
        time.sleep(2) # PAUSA 2s (para ver a volta)

    print("\n--- TODOS OS CENÁRIOS CONCLUÍDOS ---")

except Exception as e:
    print(f"\n--- O TESTE FALHOU ---")
    print(f"Erro: {e}")
    print("Verifique os IDs, o fluxo ou se o servidor está rodando.")

finally:
    print("Fim do teste.")
    # A opção 'detach' manterá o navegador aberto.
    # driver.quit()