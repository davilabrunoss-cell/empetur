# Fluxo de Atualizacao

## Fase atual

Enquanto a sincronizacao automatica com a API do iPesquisa nao entra em producao, o fluxo local continua assim:

1. Atualizar os CSVs em `data/raw/empetur_bancos/`
2. Executar:

```powershell
python scripts/consolidar_empetur.py
```

3. O script atualiza:

- tabela-base consolidada
- data e hora de execucao
- resumos do dashboard
- `dashboard_payload.json`

4. A aplicacao web passa a consumir os arquivos atualizados em `data/consolidado/` e `web/public/data/`

## Fase de producao

Com a arquitetura definitiva no ar, o fluxo passa a ser:

1. `Render` chama a API do iPesquisa
2. o backend trata os questionarios e aplica as regras de negocio
3. o backend grava a base tratada no `Supabase`
4. o backend disponibiliza um endpoint de leitura para o dashboard
5. o dashboard publicado no `Cloudflare Pages` consome os dados consolidados sem depender de arquivos versionados

## Regras de operacao

- os dados operacionais nao devem ser versionados no GitHub
- o GitHub deve receber apenas alteracoes de estrutura e codigo
- atualizacoes futuras devem ser feitas com o dashboard em uso pela equipe
