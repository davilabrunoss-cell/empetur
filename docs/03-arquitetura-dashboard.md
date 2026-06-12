# Arquitetura do Dashboard

## Stack oficial

- `Cloudflare Pages`: hospedagem do frontend em producao
- `Render`: backend de sincronizacao com a API do iPesquisa
- `Supabase`: persistencia da base consolidada e dos estados operacionais
- `GitHub`: versionamento da estrutura, codigo e documentacao

## Responsabilidades por camada

### Cloudflare Pages

- publicar o dashboard para a equipe
- servir a aplicacao React
- consumir dados prontos para exibicao via endpoint externo

### Render

- autenticar e consumir a API do iPesquisa
- processar os 29 questionarios
- aplicar o dicionario de normalizacao
- descartar registros de teste
- gravar os dados tratados no Supabase
- expor endpoints internos de sincronizacao e leitura, se necessario

### Supabase

- armazenar a tabela-base consolidada
- armazenar status operacionais dos municipios
- armazenar historico de sincronizacao
- servir como fonte oficial do dashboard em producao

### GitHub

- armazenar apenas estrutura do projeto
- versionar frontend, backend, scripts e documentacao
- nao armazenar dados operacionais nem cargas brutas de producao

## Estrutura funcional do dashboard

### Painel inicial

- mosaico com os 31 municipios
- cards superiores de acompanhamento geral
- cards clicaveis para municipios e pesquisadores
- agrupamento visual por regiao
- tabela consolidada com filtros e download
- paineis compactos com totais por pesquisador e por questionario

### Pagina individual do municipio

- status operacional do municipio
- pesquisadores vinculados e total coletado por cada um
- total de questionarios preenchidos
- primeira coleta
- ultima coleta
- total previsto
- total por categoria
- quantidade por questionario preenchido
- tabela detalhada com exportacao

### Pagina de municipios

- resumo por status: ativos, em alerta, a iniciar e concluidos
- tabela com status, total de coletas, dias de campo e ultima coleta
- controle operacional para marcar municipio como concluido

## Fontes e artefatos atuais

- `data/consolidado/empetur_tabela_base.csv`
- `data/consolidado/resumo_municipios.csv`
- `data/consolidado/resumo_questionarios.csv`
- `data/consolidado/resumo_pesquisadores.csv`
- `data/consolidado/resumo_municipio_categoria.csv`
- `data/consolidado/dashboard_payload.json`
- `data/referencias/cadastro_municipios.csv`
- `data/referencias/total_previsto_municipios.csv`

## Modo operacional

- o dashboard passa a operar continuamente em producao
- melhorias futuras devem ser publicadas sem interromper o uso da equipe
- qualquer ajuste novo deve preservar a operacao em andamento
