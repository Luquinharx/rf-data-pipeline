import os
import csv
import glob
import sys
from tqdm import tqdm

# Forçar UTF-8 no Windows
sys.stdout.reconfigure(encoding='utf-8')


def juntar_arquivos_csv(diretorio_entrada, arquivo_saida):
    arquivos_csv = glob.glob(os.path.join(diretorio_entrada, "*.csv"))

    if not arquivos_csv:
        print("❌ Nenhum CSV encontrado para consolidação.")
        return False

    print("\n🧩 Iniciando consolidação...\n")

    try:
        with open(arquivo_saida, 'w', encoding='utf-8', newline='') as arquivo_final:
            writer = csv.writer(arquivo_final, delimiter=';')

            for arquivo in tqdm(arquivos_csv, desc="📦 Consolidando", unit="arquivo"):
                print(f"\n📄 Lendo: {os.path.basename(arquivo)}")

                with open(arquivo, 'r', encoding='latin1') as f:
                    reader = csv.reader(f, delimiter=';')
                    for linha in reader:
                        writer.writerow(linha)

        # 🔎 VALIDAÇÃO FINAL
        if os.path.exists(arquivo_saida) and os.path.getsize(arquivo_saida) > 0:
            print(f"\n✅ Arquivo consolidado criado: {arquivo_saida}")
            return True
        else:
            print("\n❌ Arquivo consolidado não foi criado corretamente.")
            return False

    except Exception as e:
        print(f"\n❌ Erro durante consolidação: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Informe o diretório de entrada.")
        sys.exit(1)

    diretorio_entrada = sys.argv[1]
    arquivo_saida = os.path.join(
        os.path.dirname(diretorio_entrada),
        "saida.csv"
    )

    sucesso = juntar_arquivos_csv(diretorio_entrada, arquivo_saida)

    if not sucesso:
        sys.exit(1)
