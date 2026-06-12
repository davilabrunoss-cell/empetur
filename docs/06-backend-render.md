# Backend para Render

## Objetivo

Preparar um servico web minimo e confiavel para o Render, com sincronizacao manual a partir do iPesquisa.

## Arquivos principais

- `backend/app.py`
- `requirements.txt`
- `render.yaml`

## Endpoints atuais

### `GET /healthz`

Retorna status simples de funcionamento.

### `GET /api/dashboard/payload`

Entrega o payload consolidado do dashboard.

Prioridade de leitura:

1. cache da ultima sincronizacao em memoria
2. `EMPETUR_PAYLOAD_URL`
3. `EMPETUR_PAYLOAD_FILE`
4. erro `503` se nenhuma fonte estiver disponivel

### `POST /api/sync/ipesquisa`

Baixa os CSVs do iPesquisa, aplica a consolidacao e atualiza o payload do dashboard.

Autenticacao esperada:

- `Basic Auth`
- `IPESQUISA_CLIENT_ID` como login
- `IPESQUISA_CLIENT_SECRET` como senha

Mapeamento de formularios:

- enviar `forms` no corpo da requisicao
- ou configurar `IPESQUISA_FORM_MAP` no ambiente

## Objetivo operacional

Com essa base, o Render ja pode:

- subir um backend valido
- expor uma URL publica
- responder ao Cloudflare Pages
- sincronizar manualmente a carga do iPesquisa
- ser evoluido depois para persistencia no Supabase sem recriar o servico
