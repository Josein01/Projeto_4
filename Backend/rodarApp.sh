#!/bin/bash

# Este script automatiza a configuração e execução do ambiente Python do backend.
# Ele deve ser executado de dentro da pasta 'Backend'.

# 1. Define o nome da pasta do ambiente virtual
VENV_DIR="venv"

# 2. Remove o ambiente virtual antigo, se existir, para garantir um ambiente limpo.
# O 'rm -rf' força a remoção recursiva sem pedir confirmação.
if [ -d "$VENV_DIR" ]; then
    echo "Removendo ambiente virtual '$VENV_DIR' existente..."
    rm -rf "$VENV_DIR"
fi

# 3. Cria um novo ambiente virtual
echo "Criando um novo ambiente virtual em '$VENV_DIR' usando python3..."
python3 -m venv $VENV_DIR

# 4. Ativa o ambiente virtual
# O 'source' executa o script no shell atual, modificando seu estado.
echo "Ativando o ambiente virtual..."
source $VENV_DIR/bin/activate

# 5. Atualiza o pip (boa prática para evitar problemas com pacotes antigos)
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

# 7. Executa o script principal do projeto
echo "Iniciando a aplicação (python3 run.py)..."
python3 run.py

# 8. Desativa o ambiente virtual quando o script 'run.py' for finalizado
# (Isso só será executado se 'run.py' terminar)
echo "Aplicação finalizada. Desativando o ambiente virtual."
deactivate
