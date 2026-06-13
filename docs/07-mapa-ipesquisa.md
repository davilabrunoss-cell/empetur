# Mapa de Questionarios do iPesquisa

## Origem

Arquivo lido em:

- `C:\Users\luna_\Codex_Luna\planejamentos\Dashboard de Pesquisa\data\Lista de Questionários e Códigos (ID).xlt`

## Questionarios suportados no backend

```json
{
  "Atrativos Culturais": 9055,
  "Atrativos Naturais": 9035,
  "Sistema Marítimo e Fluvial": 8933,
  "Sistema Aéreo": 8932,
  "Sistema Rodoviário": 8931,
  "Sistema Médico-Hospitalar": 8930,
  "Sistema de Segurança": 8928,
  "Sistemas de Comunicações": 8927,
  "Roteiros Turísticos": 8926,
  "Outros Servicos de Apoio Turistico": 8925,
  "Transportes Turisticos": 8924,
  "Informações Turísticas": 8923,
  "Compras": 8922,
  "Agenciamento": 8921,
  "Empresas Organizadoras de Eventos": 8920,
  "Locais de Convernções, Exposições e Eventos Sociais": 8919,
  "Instalações Desportivas": 8918,
  "Entretenimento": 8917,
  "Alimentação": 8916,
  "Hospedagens": 8911,
  "Folguedos, Crenças Populares": 8910,
  "Folclore-Detalhado": 8909,
  "Festas Populares e Religiosas": 8906,
  "Feiras Livres, Mercados Públicos": 8905,
  "Feiras e Exposições": 8904,
  "Gastronomia-Detalhado": 8903,
  "Artesãos, Artistas Plásticos": 8901,
  "Artesanato-Detalhamento": 8900,
  "Artesanato, Folclore, Gastronomia": 8899
}
```

## Regras complementares informadas pelo projeto

- `Sistema Marítimo e Fluvial`
  - municipio: `P0. Município`
  - nome: `1. Nome do sistema marítmo ou fluvial`
  - categoria: nome do questionário
- `Sistema Aéreo`
  - municipio: `P0. Municúpio`
  - nome: `P0.1. Nome do sistema aéreo`
  - categoria: nome do questionário
- `Sistemas de Comunicações`
  - municipio: `P0. Município`
  - categoria: `1. Tipo da categoria`
  - nome: `P1.1. Nome do sistema de comunicação`
- `Informações Turísticas`
  - municipio: `P0. Município`
  - categoria: `1. Tipo da categoria`
  - nome: `P1.1. Nome do posto de informações turísticas`
- `Empresas Organizadoras de Eventos`
  - municipio: `P0. Município`
  - categoria: `1. Tipo da categoria`
  - nome: `P1.1. Nome da empresa`
- `Folguedos, Crenças Populares`
  - municipio: `P0. Município`
  - categoria: `1. Tipo da categoria`
  - nome: `P1.1. Nome do atrativo`

## Observacao importante

- o `ID Ipesquisa` e o `Codigo da Pesquisa` usado na API
- ele nao tem relacao com o identificador interno do Pipefy presente no nome antigo dos arquivos
