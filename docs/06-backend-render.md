# Backend para Render

## Objetivo

Preparar um servico web minimo e confiavel para o Render, sem depender ainda da sincronizacao final com o iPesquisa.

## Arquivos principais

- `backend/app.py`
- `requirements.txt`
- `render.yaml`

## Endpoints iniciais

### `GET /healthz`

Retorna status simples de funcionamento.

### `GET /api/dashboard/payload`

Entrega o payload consolidado do dashboard.

Prioridade de leitura:

1. `EMPETUR_PAYLOAD_URL`
2. `EMPETUR_PAYLOAD_FILE`
3. erro `503` se nenhuma fonte estiver disponivel

### `POST /api/sync/ipesquisa`

Endpoint reservado para a proxima fase de sincronizacao.

## Objetivo operacional

Com essa base, o Render ja pode:

- subir um backend valido
- expor uma URL publica
- responder ao Cloudflare Pages
- ser evoluido depois para iPesquisa + Supabase sem recriar o servico
