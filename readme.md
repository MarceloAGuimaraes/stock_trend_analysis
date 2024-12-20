# A recommender system to Buy-and-Hold Investors

Esse projeto contém um sistema de recomendação que utiliza de mais de 40 anos de dados de relatórios, balanços contábeis e análises financeiras para recomender ações. São escolhidas as melhores empresas disponíveis e, as que mais se assemelham com as empresas que o usuário já possui em seu portfólio, são recomendadas.

O foco do trabalho é em recomendar ações para investidores conhecidos como Buy-and-holders.
Buy-and-hold é é uma estratégia de investimento de longo prazo na qual os investidores adquirem ativos financeiros, especialmente ações, com a intenção de mantê-los por um período significativo de tempo, geralmente anos ou décadas. Nesta estratégia, não existe interesse em realizar lucros através da venda de ações.


## Getting Started

**1. Dataset :**

Para o dataset pronto, acesse: https://drive.google.com/drive/u/0/folders/1wAL7pEST0MeCtJytRNbGba2mez_nBwK5
Faça o download e mova os arquivos para a pasta **data**.

Se desejar construir o arquivo sumarizado de análises do zero:

1. faça o download do arquivo ** nasdaq_companies_metadata.csv **, no link do drive

2. Crie um arquivo keys.csv baseado no template [keys](keys.tmp.csv) 

3. Adicione sua API key registrada no site: [FinancialModellingPrep API](https://site.financialmodelingprep.com/developer/docs/dashboard)

4. Rode o script [Script para preprocessar os dados](lib/stock_data_process.py).

**2. Para chamar o recomendador em produção:**

  - curl https://ficaaiofeedback.fun/fica_ai_o_feedback/get_stocks_recommendations?stocks=AMZN,APPL&number_of_recommendations=5&number_of_top_companies=15


Os parâmetros a serem enviados:

*stocks:* As ações que você possui em carteira separadas por vírgula. Exemplo: stocks=AMZN,APPL

*number_of_recommendations:* Quantidade de recomendações que você deseja receber. Por padrão, são recomendadas 5 empreas. Exemplo: number_of_recommendations=5

*number_of_top_companies:* Quantidade de empresas selecionadas para análise de similaridade.
Quanto maior o número deste parâmetro, maior também será o risco e as novidades das recomendações. Por padrão, são utilizadas 20 empresas. Exemplo: number_of_top_companies=25

**3. Para montar o setup em sua máquina:**
[setup](setup_notes.md)

## Arquitetura

O sistema consite de três partes principais:

1. API que consome dados de duas fontes principais: FMPStatements(https://site.financialmodelingprep.com/) e da NASDAQ (https://www.nasdaq.com/). São utilizados dados de mais de 40 anos com relatórios oficiais, contábeis e análises. Somente empresas com pelo menos 4 anos de IPO são utilizados, visto que empresas com menos do que isso não possuem dados o suficiente para serem julgadas de forma apropriada.


2. Os dados são sumarizados e as empresas são ordenadas de acordo com algumas métricas.

  - Média do lucro líquido da empresa nos últimos 5 anos.

  - Anos com lucro líquido desde o IPO

  - Lucro líquido no último ano contábil

  - Crescimento do lucro líquido por ação, nos últimos 10 anos

  - Crescimento do lucro líquido por ação, nos últimos 5 anos

  - Market Cap (Número de ações daquela empresa negociadas na Bolsa de Valores multiplicado pelo valor individual de cada ação.)

  - Crescimento do lucro líquido no último ano contábil

As empresas são ordenadas na ordem listada dos atributos, com as superiores ficando no topo.
Novas métricas serão adicionadas no futuro, e provavelmente uma forma mais sofisticada de rankeamento.

3. Por último, o recomendador considera o portfólio do usuário para recomendar as melhores X ações da lista.
É utilizado um recomendador baseado em conteúdo que calcula as similaridades das empresas do portfolio do usuário com as top X empresas disponíveis de acordo com 5 características:

  - País

  - Setor

  - Indústria

  - Ano do IPO

  - Market CAP

4. As empresas com maior similaridade são retornadas.


## Resultados

Os resultados consideram o seguinte portfólio inicial (gerado randomicamente):
portofolio inicial = [LAKE, DSWL, GIFI, PANL, ALLT]

# Simulação de Monte Carlo
Utilizada a ferramenta ([Análise de portfólios](https://www.portfoliovisualizer.com/analysis))

Foi feito um T
Foram considerados três portfólios: O inicial do usuário, um após a recomendação do trabalho e outro com recomendações totalmente aleatórias.

Foi selecionado um portfólio inicial com as seguintes ações aleatórias:

## Trabalho Futuro

* Melhorar os critérios de rankeamento das melhores empresas

* Adicionar cálculos avançados de risco do portfólio (Índice de Sharpe) quando recomendando

* Integrar análises nos testes ( hoje são utilizadas plataformas de terceiros, o que limita o volume)

* Adicionar o perfil do investidor

* Suporte ao mercado de ações do Brasil


## Slides e Vídeo

- Slides:
- Vídeo: