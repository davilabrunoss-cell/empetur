# Tabela Base Consolidada

## Arquivo gerado

- Saida atual: `data/consolidado/empetur_tabela_base.csv`

## Colunas da tabela-base

| Coluna | Descricao |
| --- | --- |
| `arquivo_origem` | Nome do CSV de onde o registro foi extraido. |
| `questionario_preenchido` | Nome limpo do questionario, extraido do nome do arquivo. |
| `municipio` | Municipio do registro. |
| `categoria` | Tipo do atrativo ou, no caso de `Sistema Rodoviário`, o proprio nome do questionario. |
| `nome_atrativo` | Nome principal do atrativo, entidade, equipamento ou roteiro. |
| `pesquisador_informado` | Primeira coluna de pesquisador informada manualmente. |
| `pesquisador_sistema` | Coluna final `Pesquisador`, preservada para rastreabilidade. |
| `pesquisador` | Campo priorizado para analise no dashboard. |
| `data_inicio_coleta` | Data e hora de inicio do registro original. |
| `data_fim_coleta` | Data e hora de fim do registro original. |
| `linha_origem` | Linha do CSV original usada para rastrear o registro. |
| `data_execucao_carga` | Data em que o consolidado foi gerado. |
| `data_hora_execucao_carga` | Data e hora completas da geracao. |

