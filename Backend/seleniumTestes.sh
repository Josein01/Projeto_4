#!/bin/bash

# Este script automatiza a CONFIGURAÇÃO e EXECUÇÃO DOS TESTES do backend.
# Ele deve ser executado de dentro da pasta 'Backend'.
# Ele garante um ambiente limpo recriando o venv e reinstalando as dependências.

# 1. Define o nome da pasta do ambiente virtual
VENV_DIR="venv"

# 2. Ativa o ambiente virtual
# O 'source' executa o script no shell atual, modificando seu estado.
echo "Ativando o ambiente virtual..."
source $VENV_DIR/bin/activate

# 5. Atualiza o pip (boa prática)
echo "Atualizando o pip..."
pip install --upgrade pip

# 6. Instala as dependências listadas no requirements.txt
# Verifica se o arquivo existe antes de tentar instalar
if [ -f "requirements.txt" ]; then
    echo "Instalando dependências de requirements.txt..."
    pip install -r requirements.txt
else
    echo "Aviso: 'requirements.txt' não encontrado. Nenhuma dependência será instalada."
fi

# 7. Executa o script principal de TESTES
echo "Iniciando os testes (python3 test_fluxo_completo.py)..."
python3 test_fluxo_completo.py
