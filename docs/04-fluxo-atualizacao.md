# Fluxo de Atualizacao

1. Salvar os CSVs atualizados em `data/raw/empetur_bancos/`
2. Executar:

```powershell
python scripts/consolidar_empetur.py
```

3. O script atualiza:

- tabela-base consolidada
- data e hora de execucao
- resumos do dashboard

4. A aplicacao web passa a consumir os arquivos atualizados em `data/consolidado/`

