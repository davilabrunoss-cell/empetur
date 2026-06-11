# EMPETUR Dashboard

Aplicacao web para acompanhamento da producao de campo do projeto EMPETUR.

## Estrutura

- `data/raw/empetur_bancos/`: bancos CSV recebidos diariamente
- `data/consolidado/`: base consolidada e resumos para o dashboard
- `data/referencias/`: cadastros auxiliares, como municipios e totais previstos
- `scripts/`: consolidacao e geracao dos artefatos de dados
- `docs/`: regras de negocio, arquitetura e fluxo operacional
- `web/`: futura aplicacao web do dashboard

## Atualizacao da base

```powershell
python scripts/consolidar_empetur.py
```

## Saidas geradas

- `data/consolidado/empetur_tabela_base.csv`
- `data/consolidado/resumo_municipios.csv`
- `data/consolidado/resumo_questionarios.csv`
- `data/consolidado/resumo_pesquisadores.csv`
- `data/consolidado/resumo_municipio_categoria.csv`

