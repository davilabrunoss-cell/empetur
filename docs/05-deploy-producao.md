# Deploy em Producao

## Objetivo

Colocar o dashboard no ar imediatamente com a estrutura atual e evoluir o projeto sem interromper o uso operacional da equipe.

## Publicacao inicial

### Cloudflare Pages

- origem: repositorio `davilabrunoss-cell/empetur`
- diretorio raiz do projeto no Pages: `web`
- comando de build: `npm run build`
- diretorio de saida: `dist`
- branch de producao: `main`
- fallback de rotas SPA: arquivo `web/public/_redirects`
- variavel de ambiente: `VITE_DASHBOARD_DATA_URL`

### Resultado esperado

- o painel entra no ar com o dashboard atual
- a equipe ja consegue consultar mosaico, municipios, pesquisadores e tabelas
- melhorias futuras entram por push no GitHub
- os dados em producao passam a vir do backend, e nao do repositorio

## Backend de sincronizacao

### Render

- responsavel por consumir a API do iPesquisa
- executar a consolidacao automatica dos 29 questionarios
- aplicar regras de normalizacao e descarte de testes
- gravar a base consolidada no Supabase

### Supabase

- armazenar a tabela-base consolidada
- armazenar status operacionais dos municipios
- armazenar historico de sincronizacao

## Politica de versionamento

- subir para o GitHub apenas estrutura e codigo
- nao subir bancos brutos de producao
- nao subir dados operacionais do Supabase
- nao versionar payloads consolidados de producao no frontend

## Modo de evolucao

- o dashboard passa a ser mantido com "o carro em movimento"
- qualquer ajuste novo deve considerar retrocompatibilidade visual e operacional
- a publicacao do frontend nao deve depender de parada de uso da equipe
