import pandas as pd
import numpy as np

# ... (Linhas de importação e leitura de CSV permanecem as mesmas)

df_CADASTRO_CLIENTES_ATIVOS_INATIVOS = pd.read_csv(r"C:\Users\user_kyros125\Desktop\Script2\Temporario\111_CUC_ATIVO.csv", sep=',')
df_ESTABELECIMENTOS_BAIXADOS_RFB = pd.read_csv(r"C:\Users\user_kyros125\Desktop\Script2\2026-02\ESTABELECIMENTOS_RFB_PROCESSADO.csv", sep='|')

# ... (Linhas de merge permanecem as mesmas)

colunas_adicionais = ['CNPJ', 'SITUACAO_CADASTRAL','DATA_INICIO_ATIVIDADE','CNAE_PRINCIPAL']
df_cruzado_rfb_universo_clientes = pd.merge(df_CADASTRO_CLIENTES_ATIVOS_INATIVOS, df_ESTABELECIMENTOS_BAIXADOS_RFB[colunas_adicionais], left_on='NR_CPF_CNPJ', right_on='CNPJ', how='left')

# 1. Filtra as linhas onde as situações são diferentes (divergentes)
df_divergentes = df_cruzado_rfb_universo_clientes[
    df_cruzado_rfb_universo_clientes['SITUACAO_CADASTRAL'] != df_cruzado_rfb_universo_clientes['CD_SITUACAO_RECEITA']
].copy()

# 2. Remove as linhas que possuem valores NaN nas colunas de situação
df_divergentes_preenchidos = df_divergentes.dropna(subset=['SITUACAO_CADASTRAL', 'CD_SITUACAO_RECEITA'])

# --- NOVO PASSO: Reordenar as colunas ---

# Define a lista da ordem de colunas desejada.
# Coluna A: CNPJ (do arquivo RFB, que é a chave de cruzamento)
# Coluna B: SITUACAO_CADASTRAL (Situação da RFB)
# Coluna C: CD_SITUACAO_RECEITA (Situação do arquivo de clientes)
# Coluna D em diante: as outras colunas originais
colunas_principais = ['CNPJ', 'SITUACAO_CADASTRAL', 'CD_SITUACAO_RECEITA']

# Pega todas as outras colunas que não estão na lista principal para colocar no final
outras_colunas = [col for col in df_divergentes_preenchidos.columns if col not in colunas_principais]

# Cria a lista final de ordem de colunas
ordem_final_colunas = colunas_principais + outras_colunas

# Reordena o DataFrame
df_final_ordenado = df_divergentes_preenchidos[ordem_final_colunas]

# 3. Salva o DataFrame reordenado
df_final_ordenado.to_csv('AtualizarCUCATIVO.csv', index=False, sep='|')