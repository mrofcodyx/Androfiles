import os
import subprocess
from datetime import datetime
from multiprocessing.pool import ThreadPool
import sys
import time
import socket
import getpass

def obter_informacoes_sistema():
    nome_computador = socket.gethostname()
    nome_usuario = getpass.getuser()
    return nome_computador, nome_usuario

def salvar_log(informacoes_sistema, extensao, pasta_destino, total_arquivos, tempo_copia):
    nome_computador, nome_usuario = informacoes_sistema
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log = f"--- Log de Execução ---\nComputador: {nome_computador}\nUsuário: {nome_usuario}\nData e Hora: {data_hora}\nExtensão: {extensao}\nDestino: {pasta_destino}\nTotal de Arquivos Copiados: {total_arquivos}\nTempo de Cópia: {tempo_copia}\n\n"

    with open("log.txt", "a") as arquivo_log:
        arquivo_log.write(log)

def verificar_adb():
    try:
        subprocess.check_output(['adb', 'version'])
    except FileNotFoundError:
        print("\033[91mADB não encontrado. Certifique-se de que está instalado.\033[0m")
        exit(1)

def obter_extensao_arquivos():
    extensao = input("\033[93mDigite a extensão dos arquivos que deseja copiar (por exemplo, pdf): \033[0m").lower()
    return extensao

def obter_pasta_destino():
    pasta_destino = input("\033[93mDigite o caminho completo da pasta de destino ou pressione Enter para usar o diretório do script: \033[0m")
    if not pasta_destino:
        pasta_destino = os.path.dirname(os.path.realpath(__file__))
    return pasta_destino

def aguardar_dispositivo():
    print("\n\033[92mConecte o dispositivo Android ao PC...\033[0m")
    subprocess.call(['adb', 'wait-for-device'])
    print("\033[92mDispositivo conectado!\033[0m\n")

def verificar_conexao_dispositivo():
    try:
        subprocess.check_output(['adb', 'shell', 'echo', 'connected'])
        return True
    except subprocess.CalledProcessError:
        return False

def encontrar_arquivos(extensao, diretorio_origem):
    comando_adb = ['adb', 'shell', f'find {diretorio_origem} -type f -name *.{extensao}']
    lista_arquivos = subprocess.check_output(comando_adb, universal_newlines=True, stderr=subprocess.DEVNULL)
    return lista_arquivos.strip().split('\n')

def obter_nome_pasta_origem(caminho_arquivo):
    pasta_origem = os.path.dirname(caminho_arquivo)
    return os.path.basename(pasta_origem)

def copiar_arquivo(args):
    caminho_arquivo, pasta_destino = args
    comando_adb = ['adb', 'pull', caminho_arquivo, pasta_destino]
    subprocess.call(comando_adb, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def copiar_arquivos_organizados(lista_arquivos, pasta_destino, informacoes_sistema, extensao):
    total_arquivos = len(lista_arquivos)
    inicio_tempo = time.time()

    print("\033[94mCopiando arquivos: [", end='', flush=True)

    for i, caminho_arquivo in enumerate(lista_arquivos):
        if not verificar_conexao_dispositivo():
            print("\n\033[91mO dispositivo foi desplugado durante a cópia. Abortando.\033[0m")
            exit(1)

        nome_pasta_origem = obter_nome_pasta_origem(caminho_arquivo)
        pasta_destino_arquivo = os.path.join(pasta_destino, nome_pasta_origem)
        os.makedirs(pasta_destino_arquivo, exist_ok=True)
        copiar_arquivo((caminho_arquivo, pasta_destino_arquivo))

        # Atualiza a barra de progresso
        progresso = int((i + 1) / total_arquivos * 50)
        sys.stdout.write("\rCopiando arquivos: [{}{}] {}%".format('#' * progresso, ' ' * (50 - progresso), int((i + 1) / total_arquivos * 100)))
        sys.stdout.flush()

    fim_tempo = time.time()
    tempo_copia = round(fim_tempo - inicio_tempo, 2)

    sys.stdout.write("]\n")  # Completa a barra de progresso
    print("\033[92mArquivos copiados e organizados em pastas com base na origem para {}\033[0m".format(pasta_destino))
    print("\033[92mTotal de arquivos copiados: {}\033[0m".format(total_arquivos))
    print("\033[92mTempo de cópia: {} segundos\033[0m".format(tempo_copia))

    salvar_log(informacoes_sistema, extensao, pasta_destino, total_arquivos, tempo_copia)

def exibir_banner():
    frames = [
        r"""
                     _
     /\             | |
    /  \   _ __   __| |_ __ ___
   / /\ \ | '_ \ / _` | '__/ _ \
  / ____ \| | | | (_| | | | (_) |
 /_/    \_\_| |_|\__,_|_|  \___/

        """,
        r"""
       ⠀⠀⠀ ⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀       ⠙⢷⣤⣤⣴⣶⣶⣦⣤⣤⡾⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀       ⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀
⠀⠀⠀⠀       ⣼⣿⣿⣉⣹⣿⣿⣿⣿⣏⣉⣿⣿⣧⠀⠀              ______ _ _
⠀⠀⠀       ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇ By Mr_ofcodyx|  ____(_) |
       ⣠⣄⠀⢠⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⡄⠀⣠⣄ __________| |__   _| | ___  ___
       ⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿ __________|  __| | | |/ _ \/ __|
       ⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿           | |    | | |  __\__ \
       ⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿           |_|    |_|_|\___|___/
       ⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿
       ⠻⠟⠁⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠈⠻⠟
⠀⠀⠀⠀       ⠉⠉⣿⣿⣿⡏⠉⠉⢹⣿⣿⣿⠉⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀       ⣿⣿⣿⡇⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀       ⣿⣿⣿⡇⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀       ⠈⠉⠉⠀⠀⠀⠀⠉⠉⠁⠀⠀⠀⠀⠀
        """,
    ]

    for frame in frames:
        print("\033c")
        print("\033[1;33m")  # Cor amarela brilhante
        print(frame)
        time.sleep(1)
        print("\033[0m")  # Restaura a cor padrão

if __name__ == "__main__":
    exibir_banner()
    verificar_adb()
    aguardar_dispositivo()

    extensao = obter_extensao_arquivos()
    pasta_destino = obter_pasta_destino()
    informacoes_sistema = obter_informacoes_sistema()

    diretorio_origem = '/sdcard/'

    lista_arquivos = encontrar_arquivos(extensao, diretorio_origem)

    if not lista_arquivos:
        print("\033[91mNenhum arquivo com a extensão .{} encontrado.\033[0m".format(extensao))
    else:
        copiar_arquivos_organizados(lista_arquivos, pasta_destino, informacoes_sistema, extensao)
