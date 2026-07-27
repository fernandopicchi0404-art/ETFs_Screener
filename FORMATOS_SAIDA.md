# Formatos de saída

Este documento especifica as tabelas CSV e as abas do arquivo Excel descritas no [plano do projeto](PLANO_PROJETO.md).

## Princípios

- Uma coluna nunca terá significado implícito.
- Valores originais da fonte serão preservados.
- Ajustes ficarão em colunas separadas.
- Campo vazio será diferente de zero.
- Datas e moedas acompanharão todos os valores relevantes.
- Percentuais serão armazenados como números, sem texto.

## Aba `Ativos`

Uma linha por ação, contendo:

### Identificação

- ETF;
- ação;
- empresa;
- bolsa;
- país;
- ISIN;
- identificador ROIC;
- status do mapeamento.

### Datas e moedas

- moeda financeira;
- moeda do preço;
- ano fiscal;
- encerramento do ano fiscal;
- data do preço;
- preço da ação.

### Lucro e ações

- lucro incluindo minoritários;
- lucro dos minoritários;
- dividendos preferenciais;
- outros ajustes;
- lucro líquido;
- lucro disponível aos ordinários;
- ações básicas;
- ações diluídas;
- lucro por ação básico;
- lucro por ação diluído.

### Patrimônio e ROE

- patrimônio total;
- participação minoritária;
- capital preferencial ou híbrido;
- patrimônio ordinário final;
- patrimônio ordinário do ano anterior;
- patrimônio ordinário médio;
- ROE calculado;
- método do ROE.

### Distribuições

- dividendos ou JCP da ROIC;
- recompras brutas;
- emissões;
- recompras líquidas;
- ajuste externo de dividendos;
- ajuste externo de recompras;
- distribuições finais;
- dividendo por ação;
- recompra bruta por ação;
- recompra líquida por ação;
- dividend yield;
- gross buyback yield;
- net buyback yield;
- gross shareholder yield;
- net shareholder yield.

### Valuation e qualidade

- earnings yield;
- fonte externa;
- validado externamente;
- qualidade geral;
- tags;
- observações.

## Aba `Composicao_ETF`

- ETF;
- data da composição;
- posição original;
- nome;
- ticker informado pela gestora;
- ISIN ou identificador informado;
- tipo de ativo;
- moeda;
- quantidade;
- valor de mercado;
- peso original;
- incluído na análise;
- peso normalizado entre ações;
- motivo de exclusão.

## Aba `ETF_Consolidado`

- ETF;
- data da composição;
- data da execução;
- quantidade total de posições;
- quantidade de ações;
- peso original total das ações;
- peso de caixa;
- peso de derivativos;
- peso de recebíveis;
- peso de outros ativos;
- cobertura do ROE;
- cobertura do earnings yield;
- cobertura do dividend yield;
- cobertura do buyback yield;
- cobertura do shareholder yield;
- ROE agregado;
- earnings yield agregado;
- dividend yield agregado;
- gross buyback yield agregado;
- net buyback yield agregado;
- gross shareholder yield agregado;
- net shareholder yield agregado;
- P/L publicado pela gestora;
- P/VP publicado pela gestora;
- dividend yield publicado pela gestora;
- diferenças e comentários.

## Aba `Validacoes`

- ETF;
- ativo;
- período;
- teste;
- valor calculado;
- valor de comparação;
- diferença absoluta;
- diferença percentual;
- tolerância;
- resultado;
- fonte;
- endereço da fonte;
- comentário.

Resultados possíveis:

- `PASS`;
- `WARNING`;
- `FAIL`;
- `NOT_APPLICABLE`.

## Aba `Excecoes`

- ETF;
- ativo;
- data;
- severidade;
- tag;
- etapa;
- mensagem em português;
- impacto na métrica;
- ação recomendada;
- status;
- data de resolução.

Severidades:

- `INFO`: não impede o cálculo;
- `WARNING`: reduz a confiança;
- `BLOCKER`: impede o uso do dado.

## Aba `Ajustes`

- ETF;
- ativo;
- período;
- campo ajustado;
- valor original;
- valor do ajuste;
- valor final;
- moeda;
- fonte;
- endereço da fonte;
- justificativa;
- data da validação;
- status da revisão.

O valor original nunca será substituído. O cálculo final usará uma coluna derivada e rastreável.

## Tags iniciais

- `NON_EQUITY`;
- `MAPPING_NOT_FOUND`;
- `MAPPING_AMBIGUOUS`;
- `CURRENCY_MISMATCH`;
- `FISCAL_DATE_MISMATCH`;
- `MISSING_DIVIDEND`;
- `MISSING_BUYBACK`;
- `MANUAL_ADJUSTMENT`;
- `BASIC_SHARES_FALLBACK`;
- `ENDING_EQUITY_FALLBACK`;
- `EPS_RECONCILIATION_FAILED`;
- `NEGATIVE_EARNINGS`;
- `NEGATIVE_EQUITY`;
- `STALE_PRICE`;
- `API_RATE_LIMIT`;
- `API_PLAN_RESTRICTION`;
- `API_TEMPORARY_FAILURE`;
- `LOW_COVERAGE`.

## Arquivos CSV

Cada aba terá um CSV equivalente:

- `ativos.csv`;
- `composicao_etf.csv`;
- `etf_consolidado.csv`;
- `validacoes.csv`;
- `excecoes.csv`;
- `ajustes.csv`.

O Excel será uma camada amigável para consulta; os CSVs serão a base auditável usada pelos cálculos.
