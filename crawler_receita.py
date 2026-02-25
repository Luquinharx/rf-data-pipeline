import requests
import os
import time
import zipfile
import glob
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dateutil.relativedelta import relativedelta

sys.stdout.reconfigure(encoding='utf-8')

socket.setdefaulttimeout(15)

BASE_URL = "https://arquivos.receitafederal.gov.br/public.php/dav/files/gn672Ad4CF8N6TK/Dados/Cadastros/CNPJ/{mes}/Estabelecimentos{parte}.zip"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_THREADS = 2
PARTES = range(10)
MAX_RETRIES = 5


# ==========================================================
# UTIL
# ==========================================================

def zip_valido(caminho):
    if not os.path.exists(caminho):
        return False
    try:
        with zipfile.ZipFile(caminho, 'r') as z:
            return z.testzip() is None
    except:
        return False


# ==========================================================
# DESCOBRIR MÊS
# ==========================================================

def descobrir_mes_disponivel():
    print("\n🔎 Verificando mês disponível...\n")

    hoje = datetime.now()

    for i in range(2):
        mes_teste = (hoje - relativedelta(months=i)).strftime("%Y-%m")
        url_teste = BASE_URL.format(mes=mes_teste, parte=0)

        print(f"🔎 Testando mês: {mes_teste}")

        try:
            r = requests.head(url_teste, timeout=10)

            if r.status_code == 200:
                print(f"✅ Encontrado mês disponível: {mes_teste}")
                return mes_teste
            else:
                print(f"❌ Não disponível: {mes_teste} (Status {r.status_code})")

        except Exception as e:
            print(f"⚠️ Erro ao testar mês: {e}")

    return None


# ==========================================================
# DOWNLOAD COM RETRY + RESUME
# ==========================================================

def baixar_arquivo(mes, parte, pasta_zip):
    url = BASE_URL.format(mes=mes, parte=parte)
    nome = f"Estabelecimentos{parte}.zip"
    caminho = os.path.join(pasta_zip, nome)

    if zip_valido(caminho):
        return f"✔️ Já válido: {nome}"

    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            print(f"⬇️ Baixando {nome} (tentativa {tentativa})")

            headers = {}
            modo = "wb"
            tamanho_existente = 0

            if os.path.exists(caminho):
                tamanho_existente = os.path.getsize(caminho)
                headers["Range"] = f"bytes={tamanho_existente}-"
                modo = "ab"

            r = requests.get(url, stream=True, timeout=60, headers=headers)

            if r.status_code not in [200, 206]:
                return f"❌ Não encontrado: {nome}"

            with open(caminho, modo) as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            if zip_valido(caminho):
                return f"✅ Download OK: {nome}"
            else:
                print("⚠️ ZIP corrompido. Removendo e tentando novamente...")
                os.remove(caminho)

        except Exception as e:
            print(f"⚠️ Erro {nome}: {e}")
            time.sleep(2)

    return f"❌ Falha definitiva: {nome}"


# ==========================================================
# EXTRAÇÃO INTELIGENTE (SEM DUPLICAR)
# ==========================================================

def renomear_para_csv(pasta_csv):
    """
    Renomeia arquivos extraídos que não têm extensão .csv para .csv.
    """
    print("\n🏷️ Verificando e renomeando arquivos para .csv...\n")
    arquivos = os.listdir(pasta_csv)
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_csv, arquivo)
        
        # Ignora pastas e arquivos que já são .csv
        if os.path.isdir(caminho_origem) or arquivo.lower().endswith(".csv"):
            continue
            
        # Se for um arquivo sem extensão (comum na RFB), adiciona .csv
        novo_nome = arquivo + ".csv"
        caminho_destino = os.path.join(pasta_csv, novo_nome)
        
        try:
            if os.path.exists(caminho_destino):
                # Se já existe o arquivo .csv, remove o original sem extensão para evitar duplicidade
                os.remove(caminho_origem)
            else:
                os.rename(caminho_origem, caminho_destino)
                print(f"✏️ Renomeado: {arquivo} -> {novo_nome}")
        except Exception as e:
            print(f"⚠️ Erro ao renomear {arquivo}: {e}")


def extrair_zips(pasta_zip, pasta_csv):
    os.makedirs(pasta_csv, exist_ok=True)

    zips = glob.glob(os.path.join(pasta_zip, "*.zip"))
    csvs_existentes = glob.glob(os.path.join(pasta_csv, "*.csv"))


    if len(csvs_existentes) >= len(zips):
        print("✔️ Extração já realizada (arquivos .csv encontrados).")
        return

    print("\n📦 Iniciando extração...\n")

    for zip_path in zips:
        nome_zip = os.path.basename(zip_path)
        
    
        if not zip_valido(zip_path):
            print(f"❌ ZIP inválido ignorado: {nome_zip}")
            continue

        print(f"📦 Extraindo {nome_zip}")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(pasta_csv)
    
    # Chama a função de renomear após extrair todos
    renomear_para_csv(pasta_csv)


# ==========================================================
# MAIN
# ==========================================================

def main():
    print("\n🚀 Iniciando pipeline Receita Federal\n")

    mes = descobrir_mes_disponivel()

    if not mes:
        print("⏳ Nenhum mês disponível.")
        return

    print(f"\n📅 Mês detectado: {mes}")

    pasta_mes = os.path.join(BASE_DIR, mes)
    pasta_zip = os.path.join(pasta_mes, "zips")
    pasta_csv = os.path.join(pasta_mes, "csv")

    arquivo_consolidado = os.path.join(pasta_mes, "saida.csv")
    arquivo_final = os.path.join(pasta_mes, "ESTABELECIMENTOS_RFB_PROCESSADO.csv")

    if os.path.exists(arquivo_final):
        print("\n🏁 Mês já totalmente processado.")
        return

    os.makedirs(pasta_zip, exist_ok=True)
    os.makedirs(pasta_csv, exist_ok=True)

    # DOWNLOAD
    print("\n⚡ Iniciando downloads...\n")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [
            executor.submit(baixar_arquivo, mes, parte, pasta_zip)
            for parte in PARTES
        ]

        for future in as_completed(futures):
            print(future.result())

    # EXTRAÇÃO
    extrair_zips(pasta_zip, pasta_csv)

    # CONSOLIDAÇÃO
    if not os.path.exists(arquivo_consolidado):
        print("\n🧩 Chamando consolidação...\n")

        resultado = subprocess.run(
            ["python", "juntar_csv.py", pasta_csv]
        )

        if resultado.returncode != 0 or not os.path.exists(arquivo_consolidado):
            print("❌ Falha na consolidação.")
            return
    else:
        print("✔️ Consolidação já existe.")

    # FORMATAÇÃO
    if not os.path.exists(arquivo_final):
        print("\n⚙️ Chamando formatação...\n")

        resultado = subprocess.run(
            ["python", "formatar_csv.py", arquivo_consolidado]
        )

        if resultado.returncode != 0 or not os.path.exists(arquivo_final):
            print("❌ Falha na formatação.")
            return
    else:
        print("✔️ Arquivo final já existe.")

    print("\n🎯 PIPELINE FINALIZADO COM SUCESSO!\n")


if __name__ == "__main__":
    main()