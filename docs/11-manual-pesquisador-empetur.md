# Manual do Pesquisador EMPETUR (junho de 2026)

## Fonte e alcance

- Fonte primaria: *Novo Inventario Turistico de Pernambuco - Manual do Pesquisador*, versao junho de 2026, 102 paginas.
- Copia local preservada em `C:\Users\luna_\Codex_Luna\planejamentos\Dashboard de Pesquisa\docs\referencias\manual-empetur-pesquisador-junho-2026.pdf`.
- SHA-256 da copia: `ECEEF722AF3C39DA122E93FBA8B07ED9AA491D5D8FAC27B136EDFE4D1F5144FC`.
- O PDF nao foi adicionado ao GitHub. Este indice nao substitui a leitura da secao correspondente antes de alterar um enquadramento.
- As paginas abaixo sao as paginas do PDF, que coincidem com a numeracao impressa nas secoes citadas.

## Regras relevantes para o catalogo de previstos

1. Confirmar formulario e tipo de categoria antes de aprovar cada cadastro. O manual recomenda a ferramenta "Busca Formulario" para localizar formularios por palavra-chave (p. 15).
2. Quando um atrativo se enquadra em mais de uma categoria dentro de um formulario, o manual manda registrar um formulario para cada categoria, conforme indicado nas instrucoes de cada secao (ex.: A1 p. 24; A2.1 p. 33). Isso nao autoriza duplicar automaticamente um nome entre formularios de finalidades diferentes.
3. A2.2 lista tipos de artesanato, folclore e gastronomia do municipio; A2.6 cadastra artesao ou artista; A2.8 detalha um unico tipo de artesanato; B8 cadastra local de comercializacao (p. 15, 40, 47, 51, 78).
4. Para folclore, A2.2 e uma lista municipal; A2.3 identifica individuos ou grupos que fazem apresentacoes; A2.9 detalha a manifestacao cultural. Grupo e manifestacao devem ser distinguidos antes de prever ambos (p. 15-16, 41, 53).
5. A2.4 e para feira ou exposicao periodica/temporaria; A2.7 e para feira livre, mercado publico ou espaco permanente de comercializacao. B8 cobre estabelecimentos e locais de compras conforme suas categorias proprias (p. 16, 43, 49, 78).
6. Espaco religioso com relevancia construtiva ou historica vai em A2.1; cultos sem essa caracteristica, em geral, vao em B11 (p. 17). Bares e restaurantes vao em B2, nao em A2.2 ou A2.10, que tratam de expressoes gastronomicas (p. 17).
7. O nome informado deve refletir aquele pelo qual o atrativo e mais conhecido pela comunidade local ou visitantes (ex.: A2.1 p. 33; A2.3 p. 41). Para conciliacao no dashboard, preservar tambem nome original, variantes e identificador interno.

O formato `Nome | CODIGO-0001` e uma convencao operacional deste projeto, **nao** uma regra do manual. Na planilha municipal, **cada linha corresponde a um questionario previsto**, nao apenas a um atrativo. Quando o mesmo local requer dois formularios, repetir o nome e o ID interno em duas linhas, com codigo completo e comentario de campo proprios. O sufixo identifica o atrativo; o codigo completo identifica a entrega prevista e deve ser unico.

Decisao operacional de Bruno em 27/10/2026: igrejas e capelas em revisao podem ter uma linha B11 para a funcao atual e outra A2.1 **condicional**. O pesquisador deve constatar e registrar o valor historico/arquitetonico antes de concluir A2.1; sem evidencia, deve consultar a supervisao. A duplicacao na lista nao comprova esse valor nem autoriza marcar ambos os formularios como realizados.

Uma opcao condicional **pode ser cadastrada no iPesquisa antes da visita**. O cadastro da opcao e a previsao na planilha nao equivalem a coleta realizada. Bruno planejara uma questao-filtro para decidir a continuidade do formulario conforme a constatacao em campo; a pergunta, os pulos e o tratamento no dashboard ainda precisam ser definidos antes de configurar esse fluxo.

Para conciliar coletas ja realizadas com opcoes previstas, exigir o mesmo municipio e o mesmo formulario, alem de confirmar que os nomes designam a mesma entidade; guardar o `Nro. Identificacao` e o alias de campo junto ao codigo interno. Bruno confirmou 28 aliases nessa condicao em 28/10/2026. Um nome relacionado coletado em **outro formulario** deve permanecer como observacao e nao conclui automaticamente a opcao prevista. Nomes genericos sem unidade identificavel, como `Garagem` e `restaurante`, nao devem gerar codigos apenas porque aparecem no banco. O cadastro de uma nova opcao a partir de coleta anterior deve manter a origem `iPesquisa` distinta da planilha bruta de atrativos.

Na inclusao complementar de 28/10/2026, **Comunidade Quilombola** foi prevista em A2.1 (com nome proprio ainda a identificar) e **4o Encontro de Tiradeiras de Renovacao da Chapada da Uniao** em A2.5, embora as respectivas coletas antigas tenham usado A2.3. A previsao segue o objeto descrito pelo manual; essas coletas permanecem como evidencia historica em formulario diverso, sem encerrar A2.1 ou A2.5. Pousada Trevo foi prevista em B1 com grafia ainda a confirmar. Dois nomes de pousada Gonzaga em Exu receberam linhas distintas provisoriamente, mas a identidade de cada unidade deve ser conferida antes do cadastro das opcoes.

## Procedimento para os proximos municipios

1. **Preservar a fonte.** Nao editar a planilha bruta recebida. Registrar municipio, nome original, descricao, questionario sugerido e linha de origem em cada proposta derivada.
2. **Identificar o atrativo antes de gerar opcoes.** Normalizar o nome sem apagar variantes conhecidas. Verificar possiveis nomes diferentes para o mesmo local dentro do municipio. Atribuir um ID numerico global novo somente a um atrativo ainda nao catalogado; nunca reiniciar a sequencia por municipio ou formulario.
3. **Separar entidade e entrega.** O ID numerico identifica o atrativo. Cada par formulario + ID gera um codigo completo e uma linha propria na planilha municipal. O mesmo ID pode se repetir; o codigo completo nao. A contagem de questionarios previstos e a futura conciliacao com coletas devem usar o codigo completo, nao o numero de nomes distintos.
4. **Classificar cada formulario pelo que ele registra.** A2.3 descreve grupo/individuo; A2.9, manifestacao. A2.7 descreve a feira livre; B8 so entra para atividade ou estabelecimento de compras distinto. A2.4 descreve feira/exposicao periodica; B5, o espaco de eventos. A2.2 e listagem municipal; A2.8 exige tipo artesanal especifico. Nao duplicar formularios apenas porque um nome parece abranger duas categorias.
5. **Escrever comentario por linha.** O comentario deve dizer o que observar ou preencher naquele formulario, qual evidencia falta e quando consultar a supervisao. Em igrejas e capelas, B11 registra a funcao atual; A2.1 fica condicional a constatacao historica/arquitetonica. Uma linha condicional representa trabalho a decidir, nao coleta concluida.
6. **Manter um unico catalogo mestre.** Gerar as planilhas por municipio e por questionario do mesmo conjunto de opcoes. Ao corrigir formulario, manter o ID do atrativo, registrar o codigo anterior como descartado/reservado e nao atribui-lo a outra entidade. Uma opcao condicional pode ser cadastrada no iPesquisa com a condicao documentada; a decisao de prosseguir no formulario cabe ao filtro de campo ainda a definir, nao ao simples cadastro da opcao.
7. **Conferir antes da entrega.** Comparar o conjunto de codigos completos das duas planilhas, exigir unicidade e uma unica sigla de formulario por linha. Conferir que o numero de linhas corresponde ao numero de questionarios previstos, nao ao numero de atrativos, e que comentarios condicionais foram preservados.

Em Afranio, a versao atual tem 45 atrativos e 50 linhas/questionarios previstos. Banda de Pifanos (`A2.3-0005` e `A2.9-0005`), Reisado (`A2.3-0037` e `A2.9-0037`) e igrejas (`A2.1` condicional e `B11`) ilustram a separacao. `B8-0019` para a Feira Livre tambem e condicional; `B8-0018` para Expoleite foi descartado. Artesanato de Afranio em A2.8 e Samba de Roda em A2.3 permanecem fora das opcoes ate identificar, respectivamente, um tipo artesanal e um grupo distinto.

## Indice dos formularios

| Codigo | Assunto | Pagina inicial |
| --- | --- | ---: |
| A1 | Atrativos naturais | 24 |
| A2.1 | Atrativos culturais | 33 |
| A2.2 | Artesanato / Folclore / Gastronomia (listagem) | 40 |
| A2.3 | Folguedos / Crencas populares (grupos) | 41 |
| A2.4 | Feiras e exposicoes | 43 |
| A2.5 | Festas populares, religiosas, festivais e outros eventos | 45 |
| A2.6 | Artesaos / Artistas plasticos | 47 |
| A2.7 | Feiras livres / Mercados publicos | 49 |
| A2.8 | Artesanato - detalhamento | 51 |
| A2.9 | Folclore - detalhamento | 53 |
| A2.10 | Gastronomia - detalhamento | 54 |
| B1 | Hospedagem | 55 |
| B2 | Alimentacao | 59 |
| B3 | Entretenimento | 63 |
| B4 | Instalacoes desportivas | 66 |
| B5 | Locais de convencoes, exposicoes e eventos sociais | 70 |
| B6 | Empresas organizadoras de eventos | 73 |
| B7 | Agenciamento | 76 |
| B8 | Compras | 78 |
| B9 | Informacoes turisticas | 80 |
| B10 | Transportes turisticos | 82 |
| B11 | Outros servicos de apoio turistico | 85 |
| B12 | Roteiros turisticos | 88 |
| C1 | Sistema de comunicacoes | 90 |
| C2 | Sistema de seguranca | 92 |
| C3 | Sistema medico-hospitalar | 94 |
| C4 | Sistema rodoviario | 97 |
| C5 | Sistema aereo | 99 |
| C6 | Sistema maritimo e fluvial | 101 |

Os codigos de projeto da API do iPesquisa estao em `docs/07-mapa-ipesquisa.md`, nao no manual.

## Revisao do piloto de Afranio

- Bruno aprovou os ajustes para `Artesanato de Afranio` (A2.2), `Feira Livre de Afranio` (A2.7) e `Expoleite Afranio` (A2.4); o parque/patio da Expoleite permanece B5 em entrada propria.
- Banda de Pifanos e Reisado tem linhas A2.3 e A2.9 separadas, com comentarios distintos para grupo e manifestacao; confirmar em campo que ha duas realidades a registrar. Samba de Roda permanece A2.9 enquanto nao houver grupo identificado separadamente.
- Feira Livre de Afranio tem A2.7 para a feira e B8 condicional para estabelecimento/atividade de compras distinta da feira como um todo. O B8 nao deve duplicar o mesmo objeto de A2.7 sem evidencia.
- Expoleite Afranio permanece A2.4. A antiga sugestao B8 foi descartada; o parque/patio tem entrada B5 propria.
- As duas igrejas de Afranio receberam B11 e A2.1 condicional em linhas separadas. O enquadramento historico deve ser constatado no campo.

Essas revisoes estao nas planilhas de planejamento e no catalogo de codigos, **nao** nos questionarios do iPesquisa. Codigos substituidos permanecem reservados no historico.
