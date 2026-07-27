# Plano do projeto — análise financeira de ETFs

## 1. Objetivo

Construir um processo auditável que:

1. extraia a composição oficial de um ETF;
2. identifique apenas as posições em ações;
3. obtenha dados financeiros anuais de cada empresa na ROIC.ai;
4. calcule métricas comparáveis por ação;
5. valide os dados e registre ajustes justificados;
6. agregue as métricas usando os pesos das ações no ETF.

O primeiro teste será o **SCHY — Schwab International Dividend Equity ETF**. Ele investe fora dos Estados Unidos, tem composição oficial disponível e uma quantidade administrável de ações internacionais.

## 2. Escopo da composição

### 2.1 Separação por tipo de ativo

A composição original será preservada e classificada em:

- ações;
- caixa;
- recebíveis;
- derivativos;
- outros ativos.

O relatório mostrará o peso original de cada grupo. Somente as ações entrarão nos cálculos financeiros.

### 2.2 Normalização dos pesos das ações

Os pesos das ações serão normalizados para somarem 100%:

```text
Peso normalizado da ação =
peso original da ação ÷ soma dos pesos originais de todas as ações
```

Exemplo: se ações representarem 98% do ETF, uma posição com peso original de 4,9% terá peso normalizado de 5,0%.

Essa normalização remove caixa e outros ativos da análise, mas não esconde sua existência: o relatório de composição manterá os pesos originais.

## 3. Período e bases financeiras

Será utilizado o último exercício fiscal anual disponível para cada empresa. As datas podem ser diferentes entre países e empresas.

Para calcular patrimônio médio, também será solicitado o exercício fiscal anterior. Cada linha mostrará:

- ano fiscal;
- data de encerramento;
- data do preço;
- moeda do demonstrativo;
- moeda da cotação.

As métricas serão chamadas de **último FY**, e não TTM ou projeção.

## 4. Lucro e ações

### 4.1 Lucro disponível aos acionistas ordinários

Campo principal:

```text
is_earn_for_common
```

Ele é preferível ao lucro líquido consolidado porque procura retirar minoritários, dividendos preferenciais e outros ajustes.

Validação esperada:

```text
lucro incluindo minoritários
(-) lucro dos minoritários
(-) dividendos preferenciais
(±) outros ajustes
= lucro disponível aos ordinários
```

`is_net_income` só será usado como alternativa quando não houver minoritários nem instrumentos preferenciais relevantes. Toda substituição será marcada.

### 4.2 Ações diluídas e lucro por ação

Campos:

- ações diluídas: `is_sh_for_diluted_eps`;
- lucro por ação diluído: `diluted_eps`.

Validação:

```text
lucro disponível aos ordinários ÷ ações diluídas
≈ lucro por ação diluído
```

Se não houver ações diluídas, ações básicas poderão ser usadas apenas com uma tag de exceção.

## 5. Patrimônio e ROE

O patrimônio deve representar os acionistas ordinários controladores:

1. partir do patrimônio atribuível aos controladores;
2. retirar capital preferencial ou híbrido, quando existir;
3. não incluir participação de minoritários;
4. calcular a média entre os dois últimos encerramentos anuais.

```text
ROE =
lucro disponível aos ordinários
÷ patrimônio ordinário médio
```

Se o ano anterior não estiver disponível, o ROE com patrimônio final poderá ser calculado como provisório e será marcado como qualidade inferior.

## 6. Distribuições aos acionistas

Dividendos e recompras serão apresentados separadamente. Somá-los e chamar o resultado de “dividend yield” seria incorreto; a soma será chamada de **shareholder yield** ou **retorno ao acionista**.

### 6.1 Componentes

- dividendos e juros sobre capital próprio pagos;
- recompras brutas de ações;
- emissão de novas ações;
- recompras líquidas: recompras menos emissões;
- ajustes externos validados.

Não serão somados dois campos da ROIC que representem a mesma recompra. Será definida uma hierarquia de campos para evitar duplicidade.

### 6.2 Indicadores por ação

```text
Dividend yield =
dividendos pagos ÷ valor de mercado

Gross buyback yield =
recompras brutas ÷ valor de mercado

Net buyback yield =
(recompras brutas - emissões) ÷ valor de mercado

Gross shareholder yield =
(dividendos + recompras brutas) ÷ valor de mercado

Net shareholder yield =
(dividendos + recompras brutas - emissões) ÷ valor de mercado
```

O indicador principal recomendado será o **net shareholder yield**, pois uma empresa pode recomprar ações e simultaneamente emitir ações para remuneração de executivos. O indicador bruto também será entregue para mostrar todo o desembolso.

Os valores serão convertidos para formato por ação quando possível:

```text
dividendo por ação = dividendos ÷ ações aplicáveis
recompra líquida por ação = recompra líquida ÷ ações aplicáveis
```

### 6.3 Campos ausentes e ajustes

Campo vazio não significa zero. Casos como o JSCP da Renner demonstram que a ROIC pode não classificar corretamente distribuições específicas de alguns países.

Um ajuste externo só poderá ser aplicado quando houver fonte confiável, preferencialmente:

1. relatório anual;
2. bolsa oficial;
3. site de Relações com Investidores;
4. segunda base financeira estruturada.

O dado original nunca será sobrescrito. O ajuste terá:

- valor da ROIC;
- valor do ajuste;
- valor final;
- fonte e endereço;
- justificativa;
- data da validação;
- tag `MANUAL_ADJUSTMENT`.

## 7. Earnings Yield

```text
Earnings yield =
lucro por ação diluído ÷ preço da ação
```

Lucros negativos serão mantidos. Empresas com prejuízo não serão excluídas, pois isso melhoraria artificialmente o resultado do ETF.

## 8. Agregação no ETF

### 8.1 Earnings yield e distribuições

```text
Métrica agregada =
Σ (peso normalizado da ação × métrica da ação)
```

Isso será aplicado a:

- earnings yield;
- dividend yield;
- gross buyback yield;
- net buyback yield;
- gross shareholder yield;
- net shareholder yield.

### 8.2 ROE agregado

O ROE não será uma média simples dos ROEs individuais. Será calculado como uma participação proporcional nas empresas:

```text
ROE agregado =
lucro proporcional total
÷ patrimônio proporcional médio total
```

### 8.3 Cobertura

Cada métrica terá cobertura própria, calculada com os pesos normalizados das ações que possuem dados válidos.

- 95% ou mais: resultado confiável;
- entre 90% e 95%: resultado com ressalva;
- abaixo de 90%: não publicar como métrica principal.

Serão mostrados:

- contribuição sobre 100% das ações;
- métrica apenas das posições cobertas;
- percentual sem dados;
- lista das posições sem dados.

Dados ausentes nunca serão tratados silenciosamente como zero.

## 9. Validações

### 9.1 Testes automáticos por empresa

- lucro por ação recalculado versus `diluted_eps`;
- reconciliação de lucro dos ordinários;
- ativos versus passivos mais patrimônio;
- patrimônio dos controladores versus minoritários;
- datas fiscais consistentes;
- moedas compatíveis;
- variações anormais contra o ano anterior;
- distinção entre zero e campo ausente;
- preço não desatualizado;
- duplicidade de campos de recompra.

### 9.2 Cross-check externo

Todos os ativos terão validações internas. A validação externa começará por:

- dez maiores posições;
- posições que, juntas, representem pelo menos 50% das ações;
- todas as posições com alertas;
- todos os dividendos ou recompras suspeitos ou ausentes.

Uma validação externa automatizada para 100% dos ativos exigirá uma segunda API confiável. Até ela ser escolhida, o relatório indicará claramente quais ativos foram validados externamente.

### 9.3 Validação no nível do ETF

Os resultados serão comparados com dados publicados pela gestora, quando disponíveis:

- P/L e seu earnings yield implícito;
- P/VP;
- dividend yield;
- número de posições;
- soma dos pesos.

## 10. Arquivos e abas de saída

Os dados canônicos serão salvos em CSV e também apresentados em um arquivo Excel com abas. A especificação completa de colunas, abas e tags está em [FORMATOS_SAIDA.md](FORMATOS_SAIDA.md).

Para criar o Excel será usada posteriormente a biblioteca `openpyxl`, que apenas grava arquivos `.xlsx` localmente e não envia dados para serviços externos.

## 11. Processo técnico

1. Baixar e arquivar a composição oficial do SCHY.
2. Classificar os tipos de ativo e normalizar os pesos das ações.
3. Resolver identificadores usando ISIN, bolsa, país e moeda; nunca apenas o ticker.
4. Consultar DRE e balanço dos dois últimos exercícios e o preço mais recente.
5. Armazenar respostas brutas em cache.
6. Calcular métricas sem alterar os dados originais.
7. Executar validações e cross-checks.
8. Aplicar somente ajustes documentados.
9. Agregar as métricas.
10. Gerar CSVs, Excel e relatório de cobertura.

O cliente da API terá espera automática, retomada após interrupção, cache, limite de cinco chamadas por minuto, tratamento do `Retry-After`, tentativas controladas para erros temporários e mensagens claras para erros definitivos.

## 12. Critério de conclusão do piloto

O piloto estará concluído quando:

- a composição oficial estiver reconciliada;
- 100% das posições estiverem classificadas;
- os pesos das ações normalizadas somarem 100%;
- as métricas individuais forem rastreáveis aos campos originais;
- cobertura e exceções estiverem explícitas;
- os ajustes tiverem fonte;
- os agregados forem comparados com a gestora;
- o processo puder ser repetido sem baixar novamente dados ainda válidos.
