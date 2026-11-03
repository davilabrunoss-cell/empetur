# Auditoria dos questionarios EMPETUR no iPesquisa - 03/11/2026

## Escopo e metodo

Inspecao somente de leitura dos 29 projetos listados em `docs/07-mapa-ipesquisa.md`, pelo wizard do iPesquisa. Foram conferidos nome atual da pesquisa, cabecalhos das perguntas iniciais, tipo da pergunta municipal e tipo dos campos de nome. Nenhuma pergunta, opcao ou regra foi editada nesta auditoria.

Todos os 29 projetos tem `P0. Municipio` como **Lista de opcoes** com os mesmos 31 municipios, de Afranio a Trindade. Portanto, reutilizar P0; nao criar uma segunda pergunta municipal nesses projetos. Todos os campos de nome listados abaixo sao **Texto aberto**. Os campos antigos e os dados historicos devem ser preservados.

| Formulario | Projeto | Campo(s) de nome identificado(s) no inicio do questionario | Observacao |
| --- | ---: | --- | --- |
| A1 | 9035 | 3. Nome do Atrativo | Pesquisa marcada `Para Revisar` no titulo atual. |
| A2.1 | 9055 | 3. Nome do Atrativo | Ja ha regras de ocultacao por categoria e situacao. |
| A2.2 | 8899 | 3. Nome do Atrativo | Formulario de listagem de artesanato, folclore e gastronomia. |
| A2.3 | 8910 | P1.1. Nome do atrativo; 3. Nome do Atrativo | Dois campos: conferir exportacao e regras antes de ocultar qualquer um. |
| A2.4 | 8904 | 3. Nome do Atrativo |  |
| A2.5 | 8906 | 3. Nome do Atrativo |  |
| A2.6 | 8901 | 3. Nome do Atrativo |  |
| A2.7 | 8905 | 3. Nome do Atrativo |  |
| A2.8 | 8900 | 3. Nome do Atrativo |  |
| A2.9 | 8909 | 3. Nome do Atrativo |  |
| A2.10 | 8903 | 3. Nome do Atrativo |  |
| B1 | 8911 | 3. Nome |  |
| B2 | 8916 | 3. Nome |  |
| B3 | 8917 | 3. Nome |  |
| B4 | 8918 | 3. Nome |  |
| B5 | 8919 | 3. Nome |  |
| B6 | 8920 | P1.1. Nome da empresa; 3. Nome / Entidade | Dois campos: conferir exportacao e regras antes de ocultar qualquer um. |
| B7 | 8921 | 3. Nome / Entidade |  |
| B8 | 8922 | 3. Nome / Entidade |  |
| B9 | 8923 | P1.1. Nome do posto de informacoes turisticas; 3. Nome / Entidade | Dois campos: conferir exportacao e regras antes de ocultar qualquer um. |
| B10 | 8924 | 3. Nome / Entidade |  |
| B11 | 8925 | 3. Nome / Entidade |  |
| B12 | 8926 | 2. Nome do roteiro turistico | Nome fica na questao 2, nao na 3. |
| C1 | 8927 | P1.1. Nome do sistema de comunicacao; 3. Nome / Entidade | Dois campos: conferir exportacao e regras antes de ocultar qualquer um. |
| C2 | 8928 | 3. Nome / Entidade |  |
| C3 | 8930 | 2. Nome / Entidade | Nome fica na questao 2, nao na 3. |
| C4 | 8931 | 2. Nome | Ha pergunta previa `1. Terminal Rodoviario` (Sim/Nao). |
| C5 | 8932 | P0.1. Nome do sistema aereo; 3. Nome do Aeroporto | Dois campos e possivel ramificacao por equipamento; nao ocultar ambos sem verificar regras. |
| C6 | 8933 | 1. Nome do sistema maritimo ou fluvial | Nome fica na questao 1; formulario ainda desativado na sincronizacao padrao documentada. |

## Recursos verificados no wizard

- O editor de opcoes informa que e possivel incluir ou colar uma lista, com identificador e descricao; o iPesquisa gera seus proprios IDs. O codigo operacional deve permanecer no rotulo `Nome | FORMULARIO-NNNN`, nao ser substituido pelo ID da plataforma.
- A etapa `Pulos, Saltos e Regras` oferece a acao `Esconder pergunta(s)` e ja contem regras em uso no projeto 9055. A pagina separada `Filtro de opcoes de pergunta` permite apresentar opcoes conforme a resposta de outra pergunta. A configuracao concreta P0 -> atrativos ainda nao foi criada nem testada.
- Antes de aplicar a lista fechada, usar os CSVs e as regras auditadas para decidir qual campo antigo sera a referencia de cada formulario. Nos cinco projetos com dois campos de nome, a decisao deve considerar ambos. A sincronizacao do dashboard deve ler a nova resposta codificada e continuar aceitando as coletas historicas e a resposta textual de `Outro`.
- Na lista do iPesquisa ha ainda o projeto **8799**, `#1265803711 | EMPETUR - 2026`, com a descricao `Formulario de confirmacao de pontos turisticos` e **zero coletas**. Ele nao esta entre os 29 do mapa, tem estrutura propria (`1. Cidade`, `Atrativos`, `2- Nome do Atrativo`) e deve ficar fora desta alteracao ate decisao especifica.

## Regras e CSVs conferidos em 03/11/2026

Na etapa `Pulos, Saltos e Regras`, foram conferidas **78 regras** nos 29 projetos. Predominam regras `Esconder pergunta(s)`. O projeto 8906 (A2.5) tambem usa `Saltar para a pergunta`: a resposta `INATIVO` salta para `11. Pesquisador`; por isso, uma nova pergunta de atrativo deve ser posicionada e testada considerando esse fluxo. Nenhuma regra existente identificada usa os campos antigos de nome como condicao ou destino. Isso nao substitui o teste pratico dos filtros de opcoes, que sao configurados em tela separada.

O botao `Exportar coletas no formato CSV` foi usado na pagina de exportacao de cada projeto com registros, com selecao de todas as coletas. Os **28 CSVs**, com **1.479 registros** no total, estao em `C:\Users\luna_\Desktop\EMPETUR_CSV_Auditoria_2026-11-03\`, nomeados por ID e formulario. Todos foram lidos com codificacao Windows-1252 e um parser que aceita cabecalhos repetidos; nao houve linha malformada. O projeto 8933 (C6) nao tem coletas, e o iPesquisa nao gerou CSV vazio.

| Formulario | Projeto | Regras | Linhas no CSV |
| --- | ---: | ---: | ---: |
| A1 | 9035 | 4 | 76 |
| A2.1 | 9055 | 12 | 217 |
| A2.2 | 8899 | 4 | 34 |
| A2.3 | 8910 | 3 | 64 |
| A2.4 | 8904 | 1 | 25 |
| A2.5 | 8906 | 2 | 129 |
| A2.6 | 8901 | 3 | 6 |
| A2.7 | 8905 | 1 | 22 |
| A2.8 | 8900 | 1 | 12 |
| A2.9 | 8909 | 1 | 25 |
| A2.10 | 8903 | 1 | 32 |
| B1 | 8911 | 11 | 128 |
| B2 | 8916 | 6 | 205 |
| B3 | 8917 | 3 | 62 |
| B4 | 8918 | 2 | 48 |
| B5 | 8919 | 3 | 49 |
| B6 | 8920 | 2 | 24 |
| B7 | 8921 | 2 | 32 |
| B8 | 8922 | 2 | 104 |
| B9 | 8923 | 2 | 9 |
| B10 | 8924 | 2 | 19 |
| B11 | 8925 | 2 | 13 |
| B12 | 8926 | 1 | 47 |
| C1 | 8927 | 1 | 6 |
| C2 | 8928 | 1 | 25 |
| C3 | 8930 | 1 | 50 |
| C4 | 8931 | 2 | 13 |
| C5 | 8932 | 0 | 3 |
| C6 | 8933 | 2 | 0 (sem arquivo) |

Nos cinco formularios com dois campos de nome, ambos estao preenchidos em todos os registros exportados. Em A2.3 (8910), **19 de 64** pares divergem; em B9 (8923), **6 de 9**; em C1 (8927), **5 de 6**. Em B6 (8920), os 24 pares coincidem, e em C5 (8932), os 3 pares coincidem. Portanto, preservar os dois campos historicos e nao assumir equivalencia automatica, sobretudo em A2.3, B9 e C1. Os demais formularios tambem tem raras respostas sem nome no campo principal; a conciliacao deve tolerar esses casos.

O fluxo de gravacao informado por Bruno e em duas camadas: cada pergunta editada deve ser salva individualmente e a nova versao do questionario so e consolidada ao avancar todas as fases do wizard ate o final. **Nesta auditoria nenhuma pergunta, regra ou versao foi alterada/salva.** Antes de implementar, registrar o estado anterior, aplicar um piloto, percorrer o fluxo de gravacao completo e validar o formulario publicado e o CSV apos a mudanca.

## Preparacao das edicoes

Antes do piloto, em 03/11/2026, os 29 titulos foram prefixados com o codigo do formulario e verificados nos paines do iPesquisa; as contagens de coletas permaneceram em 1.479 no total. Naquela etapa nenhuma pergunta ou regra foi alterada. O CSV de prova baixado apos a mudanca recebeu o nome `C5 - #1265803711 _ EMPETUR - Sistema Aéreo - NOVO.csv`.

O passo seguinte previsto era um piloto com lista fechada/`Outro`, filtro por P0 e teste do CSV e da sincronizacao, antes de aplicar as mudancas aos demais projetos sem apagar perguntas ou dados antigos.

## Piloto A2.4 em 03/11/2026

O projeto **8904 (A2.4, Feiras e Exposicoes)** recebeu uma pergunta de selecao unica `Atrativo previsto. Selecione o item da lista do municipio ou Outro.` logo apos `P0. Municipio`. Foram cadastradas as opcoes `Expoleite Afranio | A2.4-0018`, `ExpoMarco - Festival e Feira Agropecuaria | A2.4-0079`, `Feira do Queijo | A2.4-0080` e `Outro atrativo nao listado`. Os rotulos reais no iPesquisa preservam a acentuacao do catalogo.

O filtro de opcoes tem **31 condicoes explicitas**, uma para cada municipio de P0: Afranio ve seu atrativo e `Outro`; Bodoco ve seus dois atrativos e `Outro`; as outras 29 cidades veem somente `Outro`. Testes no formulario web confirmaram Afranio, Bodoco, Exu e Trindade. Uma tentativa de usar duas condicoes `Diferente` como fallback geral nao restringiu Exu; a regra experimental ainda aparece na tabela de configuracao, mas as regras explicitas foram validadas e devem ser o padrao para os proximos projetos. Nao replicar a regra combinada.

Foi criada a regra `Atrativo previsto diferente de Outro -> Esconder 3. Nome do Atrativo`. No teste web, `Outro` abriu o campo antigo, e `Feira do Queijo | A2.4-0080` avancou de `2. Situacao` diretamente para `4. Localizacao`. Nenhuma entrevista de teste foi finalizada. O editor foi percorrido ate `Concluir` apos as configuracoes. O CSV baixado depois da mudanca tem a nova coluna, a coluna antiga e as mesmas **25 coletas historicas**. A consolidacao foi preparada para priorizar a selecao codificada e preservar o texto antigo em `Outro` e nos arquivos historicos.

O piloto ficou ativo no iPesquisa antes da publicacao da adaptacao. Em 03/11/2026, o commit `666c23f` foi enviado ao `main`; Render e Cloudflare Pages confirmaram esse commit em producao. A API respondeu em `/healthz`. Ainda nao houve coleta real codificada para validar a conciliacao de ponta a ponta no painel; os testes locais cobrem o parser e a conciliacao. A regra experimental redundante de A2.4 permanece no editor, mas os 31 filtros explicitos funcionaram no formulario web.

## Expansao controlada em 03/11/2026

| Formulario | Projeto | Pergunta nova | Opcoes previstas | Filtros municipais | Teste web |
| --- | ---: | ---: | ---: | ---: | --- |
| A2.2 | 8899 | 359944 | 1 (Afranio) + Outro | 31 regras `Igual` | Afranio e Trindade; codigo esconde o nome antigo, Outro o exibe |
| B7 | 8921 | 359945 | 1 (Inaja) + Outro | 31 regras `Igual` | Inaja e Exu |
| A2.6 | 8901 | 359946 | 1 (Inaja) + Outro | 31 regras `Igual` | Inaja e Exu |
| B10 | 8924 | 359947 | 3 (Exu) + Outro | 31 regras `Igual` | Exu e Dormentes |
| B12 | 8926 | 359948 | 3 (Exu) + Outro | 31 regras `Igual` | Exu e Dormentes; codigo esconde o nome antigo da pergunta 2, Outro o exibe |
| B5 | 8919 | 359949 | 5 (Afranio, Bodoco, Exu, Dormentes) + Outro | 31 regras `Igual` | Bodoco e Inaja |
| C4 | 8931 | 359950 | 5 (Afranio, Inaja, Dormentes, Itacuruba, Belem do Sao Francisco) + Outro | 31 regras `Igual` | Itacuruba e Bodoco |
| C2 | 8928 | 359951 | 6 (Bodoco, Dormentes, Itacuruba) + Outro | 31 regras `Igual` | Bodoco e Afranio |

As perguntas foram colocadas imediatamente depois de P0. Em cada formulario foi salva a regra `Atrativo previsto diferente de Outro -> Esconder` o campo antigo de nome; nenhuma pergunta antiga foi apagada. O wizard foi avancado ate `Concluir` e o painel de cada projeto manteve a contagem anterior de coletas. Os testes web nao finalizaram entrevistas.

Em A2.2, um filtro `P0 diferente de Afranio -> Outro` foi salvo como experimento, mas **nao restringiu** Bodoco no formulario web. Os 31 filtros explicitos foram entao cadastrados; Bodoco e Trindade exibiram somente Outro. Essa regra redundante ainda aparece no editor de A2.2 e nao deve ser replicada. Para todos os demais formularios, usar apenas regras explicitas por municipio e testar um municipio com previsao e outro sem previsao.

Estado ao fim desse lote: **9 de 29** formularios com nova pergunta (incluindo A2.4). Os outros 20 ainda estavam sem a lista fechada. Quatro codigos de formulario ainda nao possuem atrativos no catalogo provisorio; nao preencher opcoes inventadas. Os cinco projetos com dois campos antigos de nome precisam de decisao individual sobre qual texto manter em `Outro`. B12, B5, C4 e C2 foram concluidos no wizard, mantendo respectivamente 47, 49, 13 e 25 coletas preexistentes no painel. Nenhuma entrevista de teste foi finalizada.

## Novo lote de formularios em 03/11/2026

| Formulario | Projeto | Pergunta nova | Opcoes previstas | Campo antigo condicionado | Coletas preservadas | Teste web de filtros |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| A2.8 | 8900 | 359952 | 7 + Outro | 3. Nome do Atrativo | 12 | Dormentes (3 itens) e Bodoco (somente Outro) |
| B8 | 8922 | 359953 | 7 + Outro | 3. Nome / Entidade | 104 | Bodoco (2 itens) e Arcoverde (somente Outro) |
| A2.7 | 8905 | 359954 | 8 + Outro | 3. Nome do Atrativo | 22 | Dormentes (2 itens) e Arcoverde (somente Outro) |
| C3 | 8930 | 359955 | 8 + Outro | 2. Nome / Entidade | 50 | Dormentes (3 itens) e Afranio (somente Outro) |
| B3 | 8917 | 359956 | 9 + Outro | 3. Nome | 62 | Bodoco (7 itens) e Afranio (somente Outro) |
| B4 | 8918 | 359957 | 12 + Outro | 3. Nome | 48 | Bodoco (7 itens) e Afranio (somente Outro) |

Em cada projeto, a nova pergunta de selecao unica foi posicionada imediatamente apos P0 e recebeu os rotulos `Nome | CODIGO` do catalogo provisorio. Foram conferidas **31 regras explicitas** `P0. Municipio Igual` por projeto, sem repetir o experimento de filtro `Diferente`. Para cidade sem item previsto na categoria, a unica opcao e `Outro atrativo nao listado`. A regra `Atrativo previsto diferente de Outro -> Esconder campo antigo` foi conferida na tabela de regras, e o wizard foi avancado ate `Concluir`. Nenhuma pergunta antiga foi apagada.

Os testes web deste lote verificaram as opcoes apresentadas em uma cidade com itens e outra sem itens por projeto. **Nao** avancaram ate o antigo campo de nome, nao enviaram entrevistas e nao baixaram novo CSV apos as edicoes; esses comportamentos ainda precisam de verificacao posterior. As contagens dos seis paineis permaneceram iguais as da auditoria anterior. Com este lote, **15 de 29** formularios tem a nova pergunta; **14** permanecem pendentes. A conciliacao de uma coleta real codificada no dashboard ainda nao foi validada de ponta a ponta.

## Quarto lote e revisao dos filtros em 03/11/2026

| Formulario | Projeto | Pergunta nova | Opcoes previstas | Campo antigo condicionado | Coletas preservadas | Teste web |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| A2.9 | 8909 | 359958 | 15 + Outro | 3. Nome do Atrativo | 25 | Afranio (3), Belem do Sao Francisco (4) e Dormentes (somente Outro); codigo pula o nome antigo e Outro o exibe |
| B1 | 8911 | 359959 | 25 + Outro | 3. Nome | 128 | Exu (13) e Itacuruba (somente Outro); codigo pula o nome antigo e Outro o exibe |
| B11 | 8925 | 359960 | 26 + Outro | 3. Nome / Entidade | 13 | Bodoco (6) e Arcoverde (somente Outro); codigo pula o nome antigo e Outro o exibe |

As tres perguntas foram inseridas apos P0. Cada uma tem 31 filtros explicitos `P0. Municipio Igual`, e a regra `Atrativo previsto diferente de Outro -> Esconder campo antigo`. Os tres wizards foram concluidos, os campos antigos permaneceram no projeto e as contagens historicas dos paineis foram preservadas. Nenhuma entrevista de teste foi enviada; nao foi baixado novo CSV neste lote.

**Cuidado com o multisseletor do iPesquisa:** clicar no corpo de `Opcoes apresentadas` depois de tres chips selecionados pode atingir o `x` de um chip e remover silenciosamente uma opcao. Em B11/Bodoco, a primeira gravacao deixou apenas 2 dos 6 itens; em A2.9/Belem do Sao Francisco, apenas 2 dos 4. As duas regras incompletas foram substituidas, selecionando cada item pelo campo de busca do multisseletor e conferindo os valores selecionados antes de `Incluir`. Os respectivos wizards foram concluidos novamente e o formulario web confirmou as listas completas. Nos proximos formularios, usar o campo de busca, nao o corpo do seletor, e comparar a regra gravada com o catalogo antes do teste.

Foi feita uma auditoria preventiva de **todos os 18 formularios ja atualizados**: para cada municipio, comparou-se a contagem de opcoes codificadas da regra `P0 Igual` com o catalogo provisorio e confirmou-se a presenca de `Outro`. Apos as duas correcoes acima, todos tem 31 regras municipais e as contagens esperadas. Esta auditoria de contagem nao substitui uma comparacao exaustiva dos rotulos/codigos nem teste de todas as 31 cidades na versao web. Estado atual: **18 de 29** formularios atualizados, **11** pendentes. Ainda falta validar em producao uma coleta real codificada na conciliacao do dashboard.

## Quinto lote em 03/11/2026

| Formulario | Projeto | Pergunta nova | Opcoes previstas | Campo antigo condicionado | Coletas preservadas | Teste web |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| A2.5 | 8906 | 359961 | 26 + Outro | 3. Nome do Atrativo | 129 | Afranio (7 itens); codigo oculta o nome, Outro o exibe; INATIVO ainda salta para 11. Pesquisador |
| A2.10 | 8903 | 359962 | 29 + Outro | 3. Nome do Atrativo | 32 | Afranio (1 item) e Dormentes (somente Outro); codigo oculta o nome, Outro o exibe |
| B2 | 8916 | 359963 | 46 + Outro | 3. Nome | 205 | Bodoco (21 itens) e Arcoverde (somente Outro); codigo oculta o nome, Outro o exibe |

As tres perguntas foram posicionadas imediatamente apos P0. Cada formulario recebeu 31 filtros explicitos `P0. Municipio Igual`, inclusive somente `Outro` para cidades sem item no catalogo. Diferentemente da auditoria anterior de contagem, neste lote todos os rotulos e codigos de cada regra gravada foram comparados exatamente com o catalogo; nao houve divergencias. A regra `Atrativo previsto diferente de Outro -> Esconder campo antigo` foi conferida na tabela de regras, e cada wizard avancou ate `Concluir`. Nenhuma pergunta antiga foi apagada.

Em A2.5, a regra preexistente `INATIVO -> Saltar para 11. Pesquisador` foi preservada e testada na versao web depois da inclusao da nova pergunta. Em B2, a primeira tentativa de incluir a regra nova nao gravou porque o seletor de condicao havia sido limpo; a condicao `Diferente` foi selecionada novamente e a regra gravada foi conferida antes de concluir. Nenhuma entrevista de teste foi enviada e nao foi baixado novo CSV neste lote.

Estado apos o lote: **21 de 29** formularios atualizados, **8** pendentes (A1, A2.1, A2.3, B6, B9, C1, C5, C6). Os cinco formularios com dois campos antigos de nome (A2.3, B6, B9, C1, C5) exigem revisao individual; B6, C1, C5 e C6 ainda nao tem itens no catalogo provisorio. A conciliacao de uma coleta real codificada no dashboard permanece sem validacao de ponta a ponta.

## Sexto lote em 03/11/2026

| Formulario | Projeto | Pergunta nova | Opcoes previstas | Coletas preservadas | Teste web |
| --- | ---: | ---: | ---: | ---: | --- |
| A1 | 9035 | 359964 | 82 + Outro | 76 | Afranio (5 itens) e Arcoverde (somente Outro); codigo oculta 3. Nome do Atrativo, Outro o exibe |
| A2.1 | 9055 | 359965 | 118 + Outro | 217 | Afranio (16 itens) e Arcoverde (somente Outro); codigo oculta 3. Nome do Atrativo, Outro o exibe |

Ambos reutilizam P0 e tem a nova pergunta de selecao unica imediatamente depois dele. Cada projeto recebeu **31 filtros explicitos** `P0. Municipio Igual`; os rotulos e codigos gravados em cada regra foram comparados exatamente com o catalogo, sem divergencias. A regra `Atrativo previsto diferente de Outro -> Esconder 3. Nome do Atrativo` foi salva sem apagar o campo antigo. Os wizards foram avancados ate `Concluir`. Em A2.1, as 12 regras preexistentes foram mantidas, totalizando 13 apos a nova regra; A1 manteve suas 4 e recebeu uma quinta. O titulo existente de A1 ainda contem `Para Revisar`; nao foi alterado neste lote.

Os testes web nao enviaram entrevistas. Nenhum CSV novo foi baixado, e a conciliacao de uma coleta real codificada no dashboard ainda nao foi validada de ponta a ponta. Estado atual: **23 de 29** formularios atualizados; pendentes A2.3, B6, B9, C1, C5 e C6. Cinco possuem dois campos historicos de nome (A2.3, B6, B9, C1, C5); B6, C1, C5 e C6 ainda nao tem itens no catalogo provisorio. Tratar cada caso antes de ocultar qualquer campo historico.
