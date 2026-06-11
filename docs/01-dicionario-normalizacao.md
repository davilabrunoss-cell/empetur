# Dicionario de Normalizacao EMPETUR

## Objetivo

Consolidar os bancos CSV da pasta `data/raw/empetur_bancos` em uma tabela-base unica para acompanhamento da producao de campo.

## Campos normalizados da base

| Campo base | Regra |
| --- | --- |
| `arquivo_origem` | Nome original do arquivo CSV. |
| `questionario_preenchido` | Texto entre o prefixo `#1265803711 _ EMPETUR - ` e o sufixo ` - <ano>.csv` ou ` - NOVO.csv`. Ex.: `Agenciamento`. |
| `municipio` | Valor da coluna `P0. Município`. |
| `categoria` | Valor da coluna de categoria do questionario. Em `Sistema Rodoviário`, usar o proprio `questionario_preenchido`. |
| `nome_atrativo` | Valor da coluna de nome principal do registro. |
| `pesquisador_informado` | Primeira coluna de pesquisador preenchida manualmente, priorizando cabecalhos com `Pesquisador:`. |
| `pesquisador_sistema` | Coluna final chamada exatamente `Pesquisador`. |
| `pesquisador` | Campo priorizado para o dashboard: usar `pesquisador_informado`; se vazio, usar `pesquisador_sistema`. |
| `data_inicio_coleta` | Valor da coluna `Data Início` do CSV bruto. |
| `data_fim_coleta` | Valor da coluna `Data Fim` do CSV bruto. |
| `linha_origem` | Numero da linha original do CSV, contando o cabecalho como linha 1. |
| `data_execucao_carga` | Data em que a consolidacao foi executada. |
| `data_hora_execucao_carga` | Timestamp completo da consolidacao. |

## Regras por grupo de colunas

### Municipio

- Padrao unico identificado: `P0. Município`

### Categoria

- Padrao principal: cabecalhos iniciados por `1. Tipo da Categoria`
- Excecao:
  - `Sistema Rodoviário`: nao existe coluna de categoria reutilizavel para o dashboard; a categoria deve repetir o nome do questionario, isto e, `Sistema Rodoviário`

### Nome do atrativo

- Variantes mapeadas:
  - `3. Nome do Atrativo...`
  - `3. Nome...`
  - `3. Nome / Entidade...`
  - `2. Nome do roteiro turístico...`
  - `2. Nome / Entidade...`
  - `2. Nome...`

### Pesquisador

- Prioridade para o campo informado manualmente:
  - primeira coluna cujo cabecalho contenha `Pesquisador:` e nao seja a coluna final exata `Pesquisador`
- Campo do sistema:
  - coluna final chamada exatamente `Pesquisador`

## Observacoes de qualidade identificadas

- Existem valores de preenchimento nao definitivo em alguns registros, como `999`, `R/N`, `Pendencia` e `Preenchimento via link`.
- Esses valores foram preservados na tabela-base para nao mascarar a realidade do campo.

