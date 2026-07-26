# 06 — Modelos de projeção de retorno

Todos os modelos aqui são a mesma identidade do [arquivo 01](01-de-onde-vem-o-retorno.md)
com graus diferentes de detalhe. Não existe modelo "melhor" — existe modelo com mais ou
menos coisas explícitas. Quanto mais explícito, mais fácil auditar onde você errou.

---

## Modelo 1 — Bogle (o "Occam's Razor")

John Bogle, fundador da Vanguard, formalizou em 1991 no *Journal of Portfolio Management* e
revisitou em 2015 com Michael Nolan ("Occam's Razor Redux").

```
Retorno nominal em 10 anos  =  dividend yield inicial
                             + crescimento do lucro
                             ± variação anualizada do P/L
```

Bogle separa os termos em dois blocos, e a nomenclatura dele é a melhor que existe:

- **Retorno de investimento** = dividend yield + crescimento do lucro. É o que a *empresa*
  entrega.
- **Retorno especulativo** = variação do P/L. É o que os *outros investidores* decidem
  pagar.

Como calcular o termo especulativo:

```
Δ(P/L) anualizado = (P/L final ÷ P/L inicial)^(1/n) − 1
```

Exemplo do próprio artigo: partindo de P/L 27,5 e assumindo 22,5 em 10 anos →
`(22,5/27,5)^(1/10) − 1 = −1,98%` ao ano.

**Quando usar:** primeira aproximação, comparação rápida entre mercados. É o modelo mais
simples que ainda está certo.

**Limitação:** ignora recompras explicitamente, e por isso subestima o retorno de mercados
com recompra líquida relevante (EUA das últimas décadas).

---

## Modelo 2 — Grinold-Kroner (o que usamos como padrão)

Richard Grinold e Kenneth Kroner (Barclays Global Investors, 2002). É Bogle com a recompra
separada e a inflação explícita:

```
E[R] ≈ (D/P − %ΔS) + (i + g_real) + %Δ(P/L)
        └─ renda ─┘   └ crescimento ┘  └ reprecificação ┘
```

| Termo | O que é | Onde obter |
| --- | --- | --- |
| `D/P` | Dividend yield do índice | Ficha do índice |
| `−%ΔS` | Recompra líquida (variação negativa do nº de ações) | Relatório do provedor do índice |
| `i` | Inflação esperada | Breakeven de inflação dos títulos indexados |
| `g_real` | Crescimento real do lucro agregado | PIB real esperado, ajustado |
| `%Δ(P/L)` | Reprecificação | Sua premissa de múltiplo terminal |

### A regra do horizonte (a parte que evita a maioria dos erros)

Premissas que fazem sentido para 10 anos ficam absurdas na perpetuidade: lucro não pode
crescer acima do PIB para sempre, recompra não pode zerar o número de ações, múltiplo não
pode subir sem limite. As únicas premissas internamente consistentes no muito longo prazo
são:

```
%ΔE = crescimento do PIB nominal
%ΔS = 0
%Δ(P/L) = 0
```

**Quanto mais longo o horizonte, mais perto desses valores as suas premissas devem estar.**

---

## Modelo 3 — TIR implícita (Damodaran)

Em vez de projetar componentes, você inverte a conta: dado o preço do índice e o fluxo de
caixa esperado (dividendos + recompras, crescidos pela expectativa de lucro), **qual taxa
de desconto iguala o valor presente ao preço de hoje?** Essa TIR é o retorno esperado
implícito no mercado.

Subtraindo o juro livre de risco, você obtém o **prêmio de risco implícito (ERP)**.

Números publicados por Aswath Damodaran:

| Data | S&P 500 | Retorno nominal esperado | Juro 10 anos | ERP implícito |
| --- | --- | --- | --- | --- |
| 01/01/2026 | 6.845,5 | **8,41%** | 4,18% | **4,23%** |
| 01/07/2026 | 7.499,4 | — | — | **4,42%** |

Contexto histórico dado pelo próprio Damodaran: o ERP de 4,23% no início de 2026 está
"quase exatamente igual à média de 1960–2025". No pico da bolha, no fim de 1999, o ERP caiu
para 2,05%.

**Vantagem deste método:** é *market-driven* e agnóstico de modelo — não depende de você
acertar o múltiplo terminal. **Desvantagem:** embute a expectativa de crescimento do
consenso, que costuma ser otimista, e não faz nenhum ajuste por valuation estar alto.

**Como usar:** como contraponto. Se o seu Grinold-Kroner dá 4% e a TIR implícita dá 8,4%, a
diferença está inteira na sua premissa de compressão de múltiplo. Isso é bom — te força a
declarar a aposta.

---

## Modelo 4 — Ancoragem no CAPE

O mais simples de todos e o mais conservador:

```
Retorno real esperado ≈ 1 ÷ CAPE   (+ ajuste)
```

Com CAPE em 41,4 (jul/2026), isso dá **2,4% real**.

O ajuste opcional: somar a diferença entre o ROE atual e o histórico (se você acredita que
a rentabilidade estrutural subiu) e/ou somar a recompra líquida. Mas cuidado — cada ajuste
é uma licença que você dá a si mesmo para achar o mercado mais barato.

**Como usar:** como piso pessimista da faixa. Se o CAPE-implícito e o Grinold-Kroner dão
resultados muito diferentes, você aprendeu onde está a sua aposta.

---

## Exemplo trabalhado: S&P 500, horizonte de 10 anos

Premissas **ilustrativas** (jul/2026). Os valores de mercado precisam ser atualizados na
data em que você for usar; o que interessa aqui é a estrutura da conta.

| Componente | Premissa | Justificativa |
| --- | --- | --- |
| Dividend yield | 1,2% | Ficha do índice |
| Recompra líquida | +1,0% | Recompras menos emissões, média recente |
| Inflação | 2,5% | Breakeven de 10 anos |
| Crescimento real do lucro | 2,0% | Perto do PIB real, sem prêmio |
| **Subtotal (retorno de investimento)** | **6,7% nominal** | |

Agora o cenário de múltiplo. Partindo de CAPE 41,4:

| Cenário | CAPE em 10 anos | Δ anual | Retorno nominal | Retorno real |
| --- | --- | --- | --- | --- |
| Múltiplo se sustenta | 41,4 | 0,0% | 6,7% | 4,1% |
| Recuo parcial | 32 | −2,5% | 4,2% | 1,7% |
| Volta à média de 25 anos | 27 | −4,2% | 2,5% | 0,0% |
| Volta à média longa | 20 | −7,0% | −0,3% | −2,7% |

*Retorno real calculado como `(1 + nominal) ÷ (1 + inflação) − 1`, com inflação de 2,5%.*

Uma ressalva metodológica honesta: o termo de crescimento parte do lucro corrente, enquanto
o CAPE usa a média de 10 anos de lucros. Misturar os dois é uma aproximação. Se a margem
atual estiver acima da média da década — que é o caso hoje —, a conta acima é
**otimista**, porque a reversão da margem já está parcialmente embutida no CAPE e seria
contada de novo no crescimento. O rigor total exige projetar lucro e múltiplo na mesma base;
para decisão de alocação, a aproximação basta desde que você saiba para que lado ela erra.

**O que a tabela mostra:** a diferença entre os cenários é de mais de 7 pontos percentuais
ao ano, e **toda ela vem de um único termo** — o único que ninguém sabe prever.

Este é o argumento inteiro deste material em uma tabela. Quando o múltiplo de entrada é
alto, o retorno da década deixa de ser determinado pelos fundamentos e passa a ser
determinado pelo humor. Não se trata de prever qual coluna vai acontecer; trata-se de saber
que você está nessa distribuição.

### Comparação com projeções institucionais (jul/2026)

| Fonte | Ativo | Projeção 10 anos (nominal) |
| --- | --- | --- |
| Damodaran (TIR implícita, jan/26) | S&P 500 | 8,4% |
| Vanguard (VCMM, jun/26) | Ações EUA | 4,2%–6,2% |
| Vanguard | Ações EUA — valor | ~7% |
| Vanguard | Desenvolvidos ex-EUA | 4,5%–6,5% |
| Vanguard | Emergentes | 2%–4% |
| Vanguard | Renda fixa EUA alta qualidade | ~4% |

Repare que instituições sérias, olhando os mesmos dados, chegam a faixas que vão de 4% a
8%. **Isso não é falha do método — é a incerteza real do problema.** Quem te der um número
único com uma casa decimal está vendendo confiança, não análise.

---

## Regras de bolso para montar a sua projeção

1. **Trabalhe com faixa, nunca com ponto.** Rode três cenários de múltiplo terminal e
   apresente os três.
2. **Nunca assuma reprecificação positiva.** Se o seu caso de investimento precisa que o
   múltiplo suba, você não está investindo em fundamento — está apostando em sentimento.
3. **Ancore o crescimento no PIB nominal.** Crescimento de lucro acima do PIB precisa de
   justificativa explícita (recompra líquida documentada, expansão de margem com causa
   identificada).
4. **Separe o que você observa do que você supõe.** Dividend yield, earnings yield, ROE,
   P/B e variação do número de ações são **observáveis**. Crescimento e múltiplo terminal
   são **suposições**. Escreva a projeção em duas colunas.
5. **Sempre subtraia o atrito no fim.** O número que interessa é o retorno **líquido de
   taxa, imposto e câmbio** — veja o [arquivo 08](08-custos-impostos-e-mecanica-do-etf.md).
6. **Compare em termos reais.** Comparar ETFs de moedas diferentes em termos nominais é
   comparar réguas diferentes.
7. **Revise anualmente, não mensalmente.** Os inputs se movem devagar. O que se move rápido
   é o preço, e reagir a preço é exatamente o que se quer evitar.

## Planilha mínima (a estrutura que replicaremos)

| Coluna | Conteúdo | Tipo |
| --- | --- | --- |
| A | Nome do ETF / índice | texto |
| B | Dividend yield | observado |
| C | Recompra líquida (`−%ΔS`) | observado |
| D | Earnings yield (E/P) | observado |
| E | CAPE | observado |
| F | ROE agregado | observado |
| G | P/B agregado | observado |
| H | Inflação esperada | premissa |
| I | Crescimento real do lucro | premissa |
| J | Múltiplo terminal — cenário base | premissa |
| K | `Δ(P/L)` anualizado | `= (J/E)^(1/10) − 1` |
| L | Retorno nominal esperado | `= B + C + H + I + K` |
| M | Atrito total anual | observado |
| N | **Retorno líquido esperado** | `= L − M` |

## Resumo do capítulo

- Bogle, Grinold-Kroner e a TIR implícita são a mesma identidade com detalhamentos
  diferentes. Use Grinold-Kroner como padrão e os outros como contraponto.
- Quanto mais longo o horizonte, mais suas premissas precisam convergir para: crescimento
  igual ao PIB nominal, emissão líquida zero e múltiplo constante.
- Com CAPE em 41,4, a diferença entre os cenários de múltiplo vale mais de 7 p.p. ao ano —
  mais do que qualquer diferença de fundamento entre ETFs.
- Faixa, sempre. Nunca ponto.
