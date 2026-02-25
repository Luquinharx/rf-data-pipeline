import pandas as pd
import csv

df_CADASTRO_CLIENTES_ATIVOS_INATIVOS = pd.read_csv(r"C:\Users\user_kyros125\Desktop\Script2\Temporario\Matera1.csv", sep=';')
df_ESTABELECIMENTOS_BAIXADOS_RFB = pd.read_csv(r"C:\Users\user_kyros125\Desktop\Script2\2026-02\ESTABELECIMENTOS_RFB_PROCESSADO.csv", sep='|')
print(df_CADASTRO_CLIENTES_ATIVOS_INATIVOS.head(10))

# especifica as colunas do df2 que deseja adicionar ao df1
colunas_adicionais = ['CNPJ', 'CNPJ_BASICO','SITUACAO_CADASTRAL','DATA_INICIO_ATIVIDADE', 'CNAE_PRINCIPAL', 'NOME_FANTASIA']
df_cruzado_rfb_universo_clientes = pd.merge(df_CADASTRO_CLIENTES_ATIVOS_INATIVOS, df_ESTABELECIMENTOS_BAIXADOS_RFB[colunas_adicionais], left_on='COD_CNPJ_CPF', right_on='CNPJ',  how='left')

print(df_cruzado_rfb_universo_clientes.head(10))
#mudou = df_cruzado_rfb_universo_clientes[df_cruzado_rfb_universo_clientes['SITUACAO_CADASTRAL'] != df_cruzado_rfb_universo_clientes['CD_SITUACAO_RECEITA']]
df_cruzado_rfb_universo_clientes.to_csv('lista_cad_1.csv', index=False, sep='|')