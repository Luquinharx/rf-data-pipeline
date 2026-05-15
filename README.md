Pipeline de Processamento de Dados da Receita Federal
Este projeto contém um conjunto de scripts Python para automatizar o download, processamento e cruzamento de dados públicos de CNPJ da Receita Federal com bases internas (CUC e Matera).

Estrutura do Projeto
Os scripts devem ser executados em uma ordem lógica para garantir que os dados estejam disponíveis para os cruzamentos finais.

1. Coleta de Dados (crawler_receita.py)
Responsável por verificar e baixar os dados mais recentes do site da Receita Federal.

Função: Baixa os arquivos ZIP de "Estabelecimentos" do mês disponível.
Saída: Arquivos ZIP e extração inicial.
2. Consolidação e Formatação (juntar_csv.py e formatar_csv.py)
Estes scripts preparam os dados brutos da Receita para uso.

juntar_csv.py: Consolida múltiplos arquivos CSV (caso o download venha fatiado) em um único arquivo.
formatar_csv.py: Lê os dados brutos, aplica cabeçalhos corretos (CNPJ, SITUACAO_CADASTRAL, etc.) e gera o arquivo mestre: ESTABELECIMENTOS_RFB_PROCESSADO.csv.
3. Cruzamento de Dados (CUC.py e matera.py)
Scripts de negócio que cruzam a base da Receita processada com arquivos internos.

CUC.py:

Entrada: Temporario/111_CUC_ATIVO.csv (Base interna) e ESTABELECIMENTOS_RFB_PROCESSADO.csv (Base RFB processada).
Processamento: Compara a SITUACAO_CADASTRAL (RFB) com a situação interna (CD_SITUACAO_RECEITA). Identifica divergências.
Saída: AtualizarCUCATIVO.csv (Lista de clientes com situações divergentes para atualização).
matera.py:

Entrada: Temporario/Matera1.csv (Base Matera) e ESTABELECIMENTOS_RFB_PROCESSADO.csv.
Processamento: Enriquece a base Matera com informações da Receita (Data de Início, CNAE, Nome Fantasia, etc.).
Saída: lista_cad_1.csv.
Como Executar
Instale as dependências: Certifique-se de ter o Python instalado e as bibliotecas necessárias (pandas, requests, tqdm, etc.):

pip install pandas requests tqdm python-dateutil numpy
Execute o Crawler (Opcional se já tiver os dados):

python crawler_receita.py
Processe a Base da Receita: Execute a formatação apontando para o arquivo baixado (o crawler geralmente chama esses passos automaticamente ou você deve rodar manualmente se tiver o arquivo bruto).

python formatar_csv.py CAMINHO_DO_ARQUIVO_BRUTO
Execute os Cruzamentos: Verifique se os arquivos de entrada (111_CUC_ATIVO.csv, Matera1.csv) estão na pasta Temporario/.

Para atualizar o CUC:

python CUC.py
Para processar o Matera:

python matera.py
Notas
O arquivo .gitignore está configurado para ignorar arquivos de dados pesados (.csv, .zip) e pastas temporárias, garantindo que apenas o código fonte seja versionado.
