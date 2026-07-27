# 05 — Dividendos e recompras: como o caixa chega até você

## 1. Dividendo não é renda extra

O erro mental mais comum do investidor brasileiro sobre dividendos: tratar o dividendo como
"um bônus que a ação paga", em cima do preço.

Não é. **Dividendo é transferência de caixa que já era seu, do balanço da empresa para a
sua conta.** No dia do pagamento, o preço da ação cai aproximadamente pelo valor do
dividendo, porque a empresa vale exatamente aquele caixa a menos. É trocar dinheiro de
bolso.

O ponto é de Miller e Modigliani (1961) e Siegel o reafirma no capítulo 5: mantidos o
investimento e o lucro, o **valor presente do fluxo de dividendos é idêntico
independentemente do payout escolhido**. Payout muda o *timing* do recebimento, não o valor.

Isso não significa que dividendo é irrelevante. Significa que ele importa por razões
**indiretas** — disciplina de capital, sinalização, imposto, comportamento do investidor —
e não porque "gera renda".

## 2. As quatro coisas que a empresa pode fazer com o lucro

Siegel lista, e a ordem de valor varia por empresa:

| Destino | Efeito no acionista |
| --- | --- |
| Pagar dividendo | Caixa direto, tributado no recebimento |
| Recomprar ações | Menos ações, mais lucro por ação para quem fica |
| Quitar dívida | Menos despesa financeira, mais fluxo futuro |
| Reinvestir em ativos produtivos | Mais lucro futuro — **se** o ROE justificar |

Siegel observa que a recompra é, do ponto de vista tributário, superior ao dividendo: o
dividendo é tributado à alíquota marginal no momento do pagamento, enquanto a recompra gera
ganho de capital que o investidor realiza quando quiser.

## 3. A métrica correta: shareholder yield

Como dividendo e recompra são economicamente equivalentes, olhar só o dividend yield é
olhar metade da conta. A métrica correta:

```
Shareholder yield = dividend yield + recompra líquida

recompra líquida = (recompras − emissões) ÷ valor de mercado
```

O termo **líquida** carrega o peso todo. Uma empresa que recompra US$ 10 bilhões e emite
US$ 9 bilhões em remuneração baseada em ações devolveu US$ 1 bilhão, não US$ 10 bilhões.

É por isso que o modelo de Grinold-Kroner usa `−ΔS` (variação do número de ações) e não
"volume de recompras": só o saldo de ações importa.

## 4. Por que a queda do dividend yield não é, sozinha, má notícia

Este é o argumento de Siegel, e ele é correto **dentro das suas condições**:

> O dividend yield atual e o crescimento futuro dos dividendos não são independentes.
> Enquanto o earnings yield não cair, reduzir o dividendo significa reter mais lucro e,
> portanto, crescer mais.

Os dados da tabela 5-1 do livro sustentam isso: o dividend yield do pós-guerra ficou 1,41
p.p. abaixo do pré-guerra, e o crescimento dos dividendos por ação ficou 1,32 p.p. acima.
A soma se manteve.

**Repare na condição embutida:** "enquanto o earnings yield não cair". Se o dividend yield
caiu porque o *preço* subiu (e não porque o payout caiu), então o earnings yield caiu
junto, e aí a queda do yield **é** má notícia. Distinguir as duas causas é essencial:

| Causa da queda do dividend yield | Earnings yield | Leitura |
| --- | --- | --- |
| Payout menor (mais retenção) | inalterado | Neutro — o retorno migra para ganho de capital |
| Preço maior (múltiplo expandiu) | **cai** | Negativo — retorno futuro esperado menor |

## 5. O papel do reinvestimento de dividendos

Siegel dá muito peso ao reinvestimento de dividendos, e o mecanismo vale entender.

No exemplo IBM × Standard Oil (1950–2003): a Standard Oil pagava 5,19% de yield contra
2,18% da IBM. Reinvestindo os dividendos, o acionista da Standard Oil acumulava muito mais
ações ao longo de 53 anos — e foi isso que virou o jogo, apesar de a IBM ter crescido mais
em receita, lucro e valor de mercado.

O efeito tem um nome informal em Siegel: **"protetor do mercado em baixa"**. Em quedas
prolongadas, o dividendo reinvestido compra mais ações a preços menores, o que acelera a
recuperação quando o mercado volta.

**Aplicação para ETFs:** a versão **acumulação** (Acc) de um ETF faz esse reinvestimento
automaticamente, dentro do fundo, sem imposto no caminho. A versão **distribuição** (Dist)
te obriga a reinvestir manualmente, e no Brasil o recebimento é fato gerador. Para quem
está na fase de acumulação, a versão Acc é quase sempre superior — ver
[arquivo 08](08-custos-impostos-e-mecanica-do-etf.md).

## 6. Cuidado com ETFs de "alto dividendo"

Um ETF que seleciona empresas pelo maior dividend yield **não é** um ETF de maior retorno
esperado. É um ETF com um viés de fator embutido, e o viés tem dois lados:

**A favor:** yield alto frequentemente vem junto com múltiplo baixo (é a mesma coisa vista
de outro ângulo, quando o payout é estável). Historicamente isso captura parte do prêmio de
valor. Siegel documenta que carteiras nos menores P/L do S&P 500 renderam quase 3 p.p. ao
ano acima do índice, enquanto as de maior P/L ficaram 2 p.p. abaixo.

**Contra:**
- **Armadilha de yield.** Yield alto pode significar preço em colapso porque o mercado
  antecipa corte de dividendo. O yield "alto" é o do dividendo que não vai mais existir.
- **Concentração setorial.** Filtros de dividendo tendem a empilhar utilities, bancos,
  telecom e energia. Você achou que comprou "renda" e comprou uma aposta setorial.
- **Ignora recompra.** Um filtro de dividendo puro exclui empresas que devolvem caixa via
  recompra — que é a forma dominante nos EUA. Filtros de *shareholder yield* são
  conceitualmente melhores.
- **Custo fiscal.** Dividendo distribuído é tributado no caminho. Um ETF de alto dividendo
  maximiza justamente o evento tributável.

**Regra:** se o objetivo é retorno total, selecione por **preço em relação ao fundamento**
(E/P, shareholder yield), não por dividendo alto.

## 7. Aplicação prática: o que extrair de um ETF

| Item | Onde encontrar | Como usar |
| --- | --- | --- |
| Dividend yield distribuído | Ficha do ETF (yield 12m) | Termo de renda da projeção |
| Dividend yield do índice | Metodologia/ficha do índice | Melhor que o do ETF, pois exclui efeitos de caixa |
| Variação do nº de ações do índice | Relatório do provedor do índice | Entra como `−ΔS` na projeção |
| Payout médio do índice | Div. yield ÷ earnings yield | Dá `b` para checar `g = ROE × b` |
| Política de distribuição | Prospecto (Acc vs Dist) | Define o custo fiscal do caminho |

Fórmula de sanidade que fecha o círculo:

```
payout = dividend yield ÷ earnings yield
```

Se o dividend yield é 1,3% e o earnings yield é 3,5%, o payout é 37%, logo `b = 63%`. Com
um ROE agregado de 18%, o crescimento sustentável máximo é `18% × 0,63 = 11,3%` ao ano
nominal. É plausível para um mercado inteiro? Provavelmente não, e a diferença te diz o
quanto o mercado está reinvestindo abaixo do ROE contábil declarado.

## Resumo do capítulo

- Dividendo é transferência de caixa, não renda adicional. O que importa é o **shareholder
  yield** (dividendo + recompra líquida).
- Yield baixo por payout baixo é neutro. Yield baixo por preço alto é ruim. São situações
  diferentes e o earnings yield distingue as duas.
- Reinvestir dividendo é o motor da capitalização; a versão acumulação do ETF faz isso sem
  atrito fiscal.
- ETF de "alto dividendo" ≠ ETF de alto retorno. Se quiser o fator, prefira shareholder
  yield ou valor explícito.
