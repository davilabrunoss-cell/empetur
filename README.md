# EMPETUR Dashboard

Aplicacao web para acompanhamento da producao de campo do projeto EMPETUR.

## Estrutura

- `data/raw/empetur_bancos/`: bancos CSV recebidos diariamente
- `data/consolidado/`: base consolidada e resumos para o dashboard
- `data/referencias/`: cadastros auxiliares, como municipios e totais previstos
- `scripts/`: consolidacao e geracao dos artefatos de dados
- `docs/`: regras de negocio, arquitetura e fluxo operacional
- `web/`: aplicacao web do dashboard

## Arquitetura oficial

- `Cloudflare Pages`: publicacao do frontend
- `Render`: sincronizacao com a API do iPesquisa
- `Supabase`: persistencia dos dados consolidados e estados operacionais
- `GitHub`: versionamento da estrutura do projeto

Os dados operacionais nao devem ser enviados ao repositório. O GitHub guarda apenas codigo, scripts e documentacao.

## Atualizacao da base

```powershell
python scripts/consolidar_empetur.py
```

## Aplicacao web

```powershell
cd web
npm install
npm run dev
```

Aplicacao local padrao:

- `http://127.0.0.1:4173`

Variavel opcional para producao:

- `VITE_DASHBOARD_DATA_URL`: endpoint HTTP que entrega o payload consolidado do dashboard

## Deploy inicial

O dashboard deve permanecer no ar e evoluir em producao.

Frontend:

- publicar o diretorio `web/` no `Cloudflare Pages`
- comando de build: `npm run build`
- diretorio de saida: `dist`
- configurar `VITE_DASHBOARD_DATA_URL` apontando para o endpoint produtivo do backend

Backend:

- publicar no `Render` a aplicacao responsavel pela sincronizacao com a API do iPesquisa
- usar o `Supabase` como base oficial do ambiente produtivo

## Saidas geradas

- `data/consolidado/empetur_tabela_base.csv`
- `data/consolidado/resumo_municipios.csv`
- `data/consolidado/resumo_questionarios.csv`
- `data/consolidado/resumo_pesquisadores.csv`
- `data/consolidado/resumo_municipio_categoria.csv`
