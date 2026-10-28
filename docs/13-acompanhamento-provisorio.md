# Acompanhamento provisorio por municipio

## Fonte e escopo

O bloco **Acompanhamento** aparece abaixo da linha do tempo na pagina municipal. Sua fonte e o retrato versionado em `web/src/data/acompanhamento-provisorio.json`, elaborado em 28/10/2026 a partir das planilhas colaborativas **Atrativos por municipio** e **Atrativos por questionario** e das decisoes registradas em `docs/12-catalogo-codigos-atrativos.md`. Abrange Afranio, Bodoco, Inaja, Exu, Dormentes, Itacuruba e Belem do Sao Francisco: 455 opcoes `atrativo + questionario`. Nao consulta as planilhas Google em tempo real.

Essa lista e provisoria e **nao** substitui a tabela `empetur_previstos_atrativos` do Supabase nem altera o card **Total previsto** e sua pagina de atrativos validados. Novas revisoes das planilhas precisam ser refletidas no JSON versionado antes do deploy.

## Conciliacao com a carga do dashboard

O painel compara as opcoes com `base_rows` da carga corrente, exclusivamente no mesmo municipio. Uma opcao aparece como **Realizado** quando o `nro_identificacao` esta na relacao confirmada para o codigo e o questionario corresponde, ou quando existe uma unica opcao com nome normalizado exatamente igual no mesmo questionario. Nomes apenas parecidos nao sao associados automaticamente. A tabela exibe primeiro as opcoes realizadas, depois as de outro questionario e por ultimo as sem vinculo, preservando a ordem original dentro de cada grupo. O mapa de `codigo_pesquisa`/questionario presente no JSON e uma fotografia dos formularios encontrados nessa analise; versoes novas de questionario exigem atualizacao do mapa para conciliacao automatica.

**Outro questionario** indica coleta nominalmente relacionada, mas em formulario diferente do previsto; essa coleta nao conclui a opcao planejada. **Sem vinculo** significa que nao houve conciliacao nesta carga, nao que a visita nao ocorreu. Itens condicionais mantem a orientacao individual e nao devem ser interpretados como obrigacao incondicional. Uma mesma unidade pode gerar opcoes diferentes para formularios diferentes, cada uma com status proprio.

Coletas nao conciliadas aparecem em uma lista de revisao, inclusive registros ambiguos, divergentes e objetos excluidos do planejamento. A carga do dashboard continua vindo do backend/Supabase; o bloco nao grava dados nem altera as planilhas, o iPesquisa ou a base de atrativos validados.

## Visualizacao publica de campo

Cada municipio tem um link `/campo/{municipio_slug}` (por exemplo, `/campo/afranio`), disponivel na tabela de municipios e na pagina municipal, onde tambem pode ser copiado. A rota mostra somente o cabecalho de leitura, municipio, tres indicadores de coleta, linha do tempo e acompanhamento. Nao mostra botao de sincronizacao, controles de status, upload/exclusao, tabela detalhada, pesquisadores ou links para outras paginas do dashboard. Para municipios ainda sem catalogo provisorio, exibe um aviso em vez da tabela de acompanhamento.

Essa e apenas uma **simplificacao de interface**, sem autenticacao nem restricao real por municipio. O frontend continua recebendo o payload completo pela API existente e as demais rotas publicas permanecem acessiveis. Nao apresentar o link como controle de privacidade ou permissao; se isso passar a ser necessario, proteger a API e as rotas em trabalho separado.

## Atualizacao

Ao aprovar mudancas no catalogo, atualizar o JSON a partir da planilha municipal, preservando codigos e observacoes por questionario; manter `realizados` apenas para vinculos confirmados e `outroFormulario` para referencias divergentes. Conferir unicidade dos codigos, equivalencia com a listagem por questionario, build do frontend e contagens por municipio antes de publicar. No retrato de 28/10/2026, a carga analisada tinha 101 coletas nesses municipios, 71 opcoes conciliadas no mesmo formulario e 22 opcoes com evidencia em outro formulario (algumas referencias divergentes apontam para mais de uma opcao).
