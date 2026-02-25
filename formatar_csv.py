import pandas as pd
import os
import sys
from tqdm import tqdm

# Forçar UTF-8 no Windows
sys.stdout.reconfigure(encoding='utf-8')

# Caminho será recebido pelo crawler
arquivo_entrada = sys.argv[1]

pasta_saida = os.path.dirname(arquivo_entrada)
arquivo_saida = os.path.join(
    pasta_saida,
    "ESTABELECIMENTOS_RFB_PROCESSADO.csv"
)

# Cabeçalho do arquivo
colunas = [
    'CNPJ_BASICO', 'CNPJ_ORDEM', 'CNPJ_DV', 'IDENTIFICADOR_MATRIZ_FILIAL', 'NOME_FANTASIA',
    'SITUACAO_CADASTRAL', 'DATA_SITUACAO_CADASTRAL', 'MOTIVO_SITUACAO_CADASTRAL',
    'NOME_DA_CIDADE_NO_EXTERIOR', 'PAIS', 'DATA_INICIO_ATIVIDADE', 'CNAE_PRINCIPAL',
    'CNAE_SECUNDARIO', 'TIPO_LOGRADOURO', 'LOGRADOURO', 'NUMERO', 'COMPLEMENTO',
    'BAIRRO', 'CEP', 'UF', 'MUNICIPIO', 'DDD1', 'TELEFONE_1', 'DDD_2', 'TELEFONE_2',
    'DDD_FAX', 'FAX', 'EMAIL', 'SITUACAO_ESPECIAL', 'DATA_SITUACAO_ESPECIAL'
]

CHUNKSIZE = 100000

def contar_linhas(arquivo):
    print("🔎 Contando linhas para calcular progresso...")
    with open(arquivo, 'r', encoding='ISO-8859-1') as f:
        return sum(1 for _ in f)


def formatar():

    if not os.path.exists(arquivo_entrada):
        print("❌ Arquivo de entrada não encontrado.")
        return False

    total_linhas = contar_linhas(arquivo_entrada)
    total_chunks = total_linhas // CHUNKSIZE + 1

    print(f"📊 Total de linhas: {total_linhas:,}")
    print(f"📦 Total de blocos (chunks): {total_chunks}")
    print("\n⚙️ Iniciando formatação...\n")

    resultado = []

    try:
        reader = pd.read_csv(
            arquivo_entrada,
            sep=';',
            encoding='ISO-8859-1',
            names=colunas,
            dtype=str,
            chunksize=CHUNKSIZE,
            low_memory=False
        )

        for chunk in tqdm(reader, total=total_chunks, desc="🔄 Processando", unit="chunk", colour="green"):

            # Construir CNPJ completo
            chunk['CNPJ'] = (
                chunk['CNPJ_BASICO'] +
                chunk['CNPJ_ORDEM'] +
                chunk['CNPJ_DV']
            )

            # Selecionar colunas desejadas
            df_filtrado = chunk[[
                'CNPJ',
                'SITUACAO_CADASTRAL',
                'CNPJ_BASICO',
                'DATA_INICIO_ATIVIDADE',
                'CNAE_PRINCIPAL',
                'NOME_FANTASIA'
            ]]

            resultado.append(df_filtrado)

        # Concatenar tudo
        print("\n🧩 Consolidando resultado final...")
        df_final = pd.concat(resultado)

        print("💾 Salvando arquivo final...")
        df_final.to_csv(arquivo_saida, sep='|', index=False)

        # Validação
        if os.path.exists(arquivo_saida) and os.path.getsize(arquivo_saida) > 0:
            print("\n✅ Arquivo final criado com sucesso!")
            print(f"📁 {arquivo_saida}")
            print(f"📊 Total de registros: {len(df_final):,}")
            return True
        else:
            print("\n❌ Arquivo final não foi criado corretamente.")
            return False

    except Exception as e:
        print(f"\n❌ Erro durante formatação: {e}")
        return False


if __name__ == "__main__":
    sucesso = formatar()

    if not sucesso:
        sys.exit(1)
