# Acompanhamento provisorio por municipio

## Fonte e escopo

O bloco **Acompanhamento** aparece abaixo da linha do tempo na pagina municipal. Sua fonte e o retrato versionado em `web/src/data/acompanhamento-provisorio.json`, elaborado em 28/10/2026 a partir das planilhas colaborativas **Atrativos por municipio** e **Atrativos por questionario** e das decisoes registradas em `docs/12-catalogo-codigos-atrativos.md`. Abrange Afranio, Bodoco, Inaja, Exu, Dormentes, Itacuruba e Belem do Sao Francisco: 455 opcoes `atrativo + questionario`. Nao consulta as planilhas Google em tempo real.

Essa lista e provisoria e **nao** substitui a tabela `empetur_previstos_atrativos` do Supabase nem altera o card **Total previsto** e sua pagina de atrativos validados. Novas revisoes das planilhas precisam ser refletidas no JSON versionado antes do deploy.

## Conciliacao com a carga do dashboard

O painel compara as opcoes com `base_rows` da carga corrente, exclusivamente no mesmo municipio. Uma opcao aparece como **Realizado** quando o `nro_identificacao` esta na relacao confirmada para o codigo e o questionario corresponde, ou quando existe uma unica opcao com nome normalizado exatamente igual no mesmo questionario. Nomes apenas parecidos nao sao associados automaticamente. A tabela exibe primeiro as opcoes realizadas, depois as realizadas em outro questionario e por ultimo as sem vinculo, preservando a ordem original dentro de cada grupo. O mapa de `codigo_pesquisa`/questionario presente no JSON cobre os 29 projetos auditados; versoes novas de questionario ainda exigem atualizacao do mapa para conciliacao automatica.

Quando uma coleta nova usa a pergunta `Atrativo previsto.`, o valor `Nome | CODIGO` passa a ser a referencia primaria. O painel concilia pelo codigo completo, no mesmo municipio e formulario; `Outro atrativo nao listado` continua usando o nome do campo textual antigo. Coletas historicas sem a nova coluna preservam a conciliacao anterior por ID confirmado ou nome exato.

**Outro questionario** indica coleta nominalmente relacionada, mas em formulario diferente do previsto; essa coleta nao conclui a opcao planejada. **Sem vinculo** significa que nao houve conciliacao nesta carga, nao que a visita nao ocorreu. Itens condicionais mantem a orientacao individual e nao devem ser interpretados como obrigacao incondicional. Uma mesma unidade pode gerar opcoes diferentes para formularios diferentes, cada uma com status proprio.

Coletas nao conciliadas aparecem em uma lista de revisao, inclusive registros ambiguos, divergentes e objetos excluidos do planejamento. A carga do dashboard continua vindo do backend/Supabase; o bloco nao altera as planilhas, o iPesquisa ou a base de atrativos validados. A unica gravacao manual do bloco e a data do Cronograma, descrita abaixo.

## Visualizacao publica de campo

Cada municipio tem um link `/campo/{municipio_slug}` (por exemplo, `/campo/afranio`), disponivel na tabela de municipios e na pagina municipal, onde tambem pode ser copiado. A rota mostra **somente o painel Acompanhamento**, com o nome do municipio no titulo e a data de atualizacao da carga. Busca e filtros continuam disponiveis dentro do painel; no celular, cada linha da tabela e apresentada como bloco. Nao mostra cabecalho do dashboard, indicadores, linha do tempo, botao de sincronizacao, controles de status, upload/exclusao, tabela detalhada, pesquisadores ou links para outras paginas. Para municipios ainda sem catalogo provisorio, exibe apenas um aviso.

Essa e apenas uma **simplificacao de interface**, sem autenticacao nem restricao real por municipio. O frontend continua recebendo o payload completo pela API existente e as demais rotas publicas permanecem acessiveis. Nao apresentar o link como controle de privacidade ou permissao; se isso passar a ser necessario, proteger a API e as rotas em trabalho separado.

## Cronograma de visita

A coluna **Cronograma**, apos **Orientacao / coleta**, mostra a data planejada por municipio e codigo do catalogo. O valor inicial e **A definir**. A pagina municipal e o link publico `/campo/{slug}` mostram as datas somente para leitura.

Cada municipio tem links privados de edicao tanto para a pagina completa `/municipio/{slug}#editar={token}` quanto para a pagina simplificada `/campo/{slug}#editar={token}`. Sem o token, ambas mostram o Cronograma somente para leitura e orientam a abrir o link privado. O token aleatorio tem 32 bytes, nao e versionado e e removido da barra de endereco ao abrir a pagina; a sessao o conserva somente em `sessionStorage`. A API recebe o token exclusivamente no cabecalho `X-Cronograma-Token`, compara seu SHA-256 com o hash cadastrado para o municipio e nunca devolve o segredo. O link deve ser compartilhado apenas com o pesquisador responsavel; quem o possuir pode alterar datas daquele municipio. Nao constitui autenticacao pessoal nem protege o restante do payload publico.

`GET /api/cronograma/{slug}` devolve datas e permissao de edicao, sem cache compartilhado. `PUT /api/cronograma/{slug}/{codigo}` aceita apenas `data_visita` no formato ISO `AAAA-MM-DD` ou `null` para limpar. O backend confere que municipio e codigo existem no catalogo versionado antes de gravar. Nome, questionario, situacao, observacao, coletas e demais campos nao sao editaveis por essa API. A persistencia usa `empetur_cronograma`; hashes de tokens ficam em `empetur_cronograma_edit_tokens`. Ambas as tabelas tem RLS ativo e nao concedem acesso a `anon` ou `authenticated`; o backend usa a chave de servico. A migracao esta em `docs/15-supabase-cronograma.sql`. Rotacionar o token de um municipio invalida o link anterior.

O catalogo ainda e provisorio. Se um codigo for removido ou alterado em uma revisao, sua data antiga permanece no banco mas deixa de aparecer no painel e nao pode ser editada ate reconciliacao explicita. Nao reutilizar codigos para outro atrativo. Os dados de cronograma nao alteram a conciliacao das coletas nem o card **Total previsto**.

## Atualizacao

Ao aprovar mudancas no catalogo, atualizar o JSON a partir da planilha municipal, preservando codigos e observacoes por questionario; manter `realizados` apenas para vinculos confirmados e `outroFormulario` para referencias divergentes. Conferir unicidade dos codigos, equivalencia com a listagem por questionario, build do frontend e contagens por municipio antes de publicar. No retrato de 28/10/2026, a carga analisada tinha 101 coletas nesses municipios, 71 opcoes conciliadas no mesmo formulario e 22 opcoes com evidencia em outro formulario (algumas referencias divergentes apontam para mais de uma opcao).
