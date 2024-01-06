#!/bin/bash

# Este script instala as dependências necessárias para executar o script principal.

# Instalação das dependências Python usando pip
echo "Instalando dependências Python..."
pip3 install -r requirements.txt

# Verifica se o ADB está instalado
if ! command -v adb &> /dev/null; then
    echo "ADB não encontrado. Tentando instalar..."

    # Tenta instalar o ADB usando o gerenciador de pacotes do sistema (apt no caso do Ubuntu)
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install android-tools-adb
    else
        # Adicione outras lógicas de instalação aqui para diferentes distribuições Linux
        echo "Erro: Não foi possível instalar o ADB automaticamente. Por favor, instale manualmente e certifique-se de que está no seu PATH."
        exit 1
    fi

    # Verifica novamente se o ADB foi instalado com sucesso
    if ! command -v adb &> /dev/null; then
        echo "Erro: ADB ainda não encontrado. Certifique-se de que está instalado e no seu PATH."
        exit 1
    fi
fi

echo "Dependências instaladas com sucesso."
