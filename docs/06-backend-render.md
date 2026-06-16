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

### `GET /api/municipios/status`

Retorna o mapa persistido dos municipios marcados como concluidos.

Prioridade de leitura:

1. tabela de status no `Supabase`, se configurado
2. arquivo local do Render, como fallback

### `PUT /api/municipios/status/{municipio_slug}`

Atualiza o status operacional persistido de um municipio.

Prioridade de gravacao:

1. tabela de status no `Supabase`, se configurado
2. arquivo local do Render, como fallback

Corpo esperado:

```json
{
  "concluido": true
}
```

### `GET /api/previstos/{municipio_slug}`

Retorna a tabela de atrativos validados do municipio.

### `PUT /api/previstos/{municipio_slug}`

Substitui integralmente a tabela de atrativos validados do municipio.

Corpo esperado:

```json
{
  "rows": [
    {
      "regiao": "SERTÃO DO MOXOTÓ",
      "municipio": "Arcoverde",
      "categoria": "Atrativos Culturais",
      "referencia": "Prefeitura",
      "atrativo": "Estação Ferroviária"
    }
  ]
}
```

### `POST /api/sync/ipesquisa`

Baixa os CSVs do iPesquisa, aplica a consolidacao e atualiza o payload do dashboard.

Autenticacao esperada:

- `Basic Auth`
- `IPESQUISA_CLIENT_ID` como login
- `IPESQUISA_CLIENT_SECRET` como senha

Mapeamento de formularios:

- enviar `forms` no corpo da requisicao
- ou configurar `IPESQUISA_FORM_MAP` no ambiente

Desativacao temporaria de formularios:

- configurar `IPESQUISA_DISABLED_FORMS` com nomes separados por virgula
- se a variavel nao existir, o backend ignora por padrao estes formularios:
  - `Sistema Marítimo e Fluvial`
  - `Sistema Aéreo`
  - `Sistemas de Comunicações`
  - `Informações Turísticas`
  - `Empresas Organizadoras de Eventos`
  - `Folguedos, Crenças Populares`

## Objetivo operacional

Com essa base, o Render ja pode:

- subir um backend valido
- expor uma URL publica
- responder ao Cloudflare Pages
- sincronizar manualmente a carga do iPesquisa
- persistir o marcador de municipio concluido no servidor
- ser evoluido depois para persistencia no Supabase sem recriar o servico

## Variaveis do Supabase para status municipal

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_SCHEMA`
  - valor sugerido: `public`
- `SUPABASE_TABLE_STATUS`
  - valor sugerido: `empetur_municipios_status`
- `SUPABASE_TABLE_PREVISTOS`
  - valor sugerido: `empetur_previstos_atrativos`
