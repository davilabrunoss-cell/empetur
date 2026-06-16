# EMPETUR Dashboard

Aplicacao web para acompanhamento da producao de campo do projeto EMPETUR.

## Estrutura

- `backend/`: API Python para publicar o payload do dashboard e receber a futura sincronizacao
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

## API backend local

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 3000
```

Endpoints atuais:

- `GET /healthz`
- `GET /api/dashboard/payload`
- `POST /api/sync/ipesquisa`
- `GET /api/municipios/status`
- `PUT /api/municipios/status/{municipio_slug}`
- `GET /api/previstos/{municipio_slug}`
- `PUT /api/previstos/{municipio_slug}`

## Variaveis principais do backend

- `EMPETUR_CORS_ORIGINS`
- `IPESQUISA_BASE_URL`
- `IPESQUISA_API_PATH`
- `IPESQUISA_CLIENT_ID`
- `IPESQUISA_CLIENT_SECRET`
- `IPESQUISA_TIMEOUT_SECONDS`
- `IPESQUISA_FORM_MAP`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_SCHEMA`
- `SUPABASE_TABLE_STATUS`
- `SUPABASE_TABLE_PREVISTOS`

`IPESQUISA_FORM_MAP` deve ser um JSON com o mapeamento entre o nome do questionario e o codigo da pesquisa no iPesquisa.

Exemplo:

```json
{
  "Atrativos Naturais": 9035,
  "Hospedagens": 9123
}
```

## Saidas geradas

- `data/consolidado/empetur_tabela_base.csv`
- `data/consolidado/resumo_municipios.csv`
- `data/consolidado/resumo_questionarios.csv`
- `data/consolidado/resumo_pesquisadores.csv`
- `data/consolidado/resumo_municipio_categoria.csv`
