# 09 — Checklist de avaliação de ETF

Este é o arquivo operacional. Os outros explicam o porquê; este diz o que fazer.

A lógica é sempre a mesma, em quatro passos:

```
1. O que o ETF realmente possui
2. Qual o fundamento e o preço desse conjunto
3. Qual retorno é razoável esperar (faixa)
4. Quanto do retorno chega até mim depois do atrito
```

---

## Bloco A — O que o ETF realmente possui

| # | Item | Onde obter | Por que importa |
| --- | --- | --- | --- |
| A1 | Índice replicado e metodologia | Ficha e site do provedor do índice | O produto é o índice ([08](08-custos-impostos-e-mecanica-do-etf.md)) |
| A2 | Nº de posições | Ficha do ETF | Diversificação nominal |
| A3 | Peso das 10 maiores | Ficha do ETF | Diversificação **efetiva** |
| A4 | Distribuição por país | Ficha do ETF | "Global" costuma ser ~62% EUA ([07](07-diversificacao-e-passivo.md)) |
| A5 | Distribuição por setor | Ficha do ETF | Explica ROE e múltiplo agregados |
| A6 | Ponderação (cap-weighted, igual, fatorial) | Metodologia do índice | Define giro e viés |
| A7 | Frequência de rebalanceamento | Metodologia do índice | Custo escondido |
| A8 | Sobreposição com o que já tenho | Comparar as 10 maiores | Evita concentração acidental |

**Alerta:** se A3 passa de ~25%, trate o ETF como uma aposta concentrada, não como
exposição ampla — independentemente de quantas posições A2 mostrar.

## Bloco B — Fundamento e preço

| # | Métrica | Fórmula / fonte | Uso na decisão |
| --- | --- | --- | --- |
| B1 | Dividend yield | Ficha do índice | Termo de renda |
| B2 | Recompra líquida (`−%ΔS`) | Relatório do provedor do índice | Termo de renda |
| B3 | Earnings yield (E/P) | `1 ÷ P/L` | Âncora do retorno real ([03](03-earnings-yield-a-ancora.md)) |
| B4 | CAPE | Preço ÷ média de 10 anos do lucro real | Âncora de longo prazo |
| B5 | P/B agregado | Ficha do índice | Junto com ROE, valida o E/P |
| B6 | ROE agregado | `E/P × P/B` ou ficha | Qualidade do reinvestimento ([04](04-roe-reinvestimento-e-crescimento.md)) |
| B7 | Payout implícito | `B1 ÷ B3` | Dá `b` para checar `g = ROE × b` |
| B8 | Crescimento do LPA, 10 anos | Série do índice | Compare com `ROE × b` do mesmo período |
| B9 | Margem líquida agregada | Ficha do índice | Margem em pico histórico é risco de reversão |
| B10 | Alavancagem agregada | Ficha do índice | ROE alavancado é ROE frágil |

**Cheques de consistência que valem ouro:**

```
E/P deve bater com  ROE ÷ (P/B)         → se não bater, os dados são de datas diferentes
payout = div yield ÷ earnings yield     → se der acima de 100%, o lucro está deprimido
g histórico ≤ ROE × b                   → se g > ROE×b, o crescimento veio de fora (M&A, dívida)
```

## Bloco C — Projeção de retorno

Aplique Grinold-Kroner do [arquivo 06](06-modelos-de-projecao.md), em **três cenários de
múltiplo terminal**:

```
E[R nominal] = (B1 + B2) + (inflação esperada + crescimento real do lucro) + Δ(P/L)
```

| Cenário | Múltiplo terminal | Interpretação |
| --- | --- | --- |
| Otimista | Mantém o múltiplo atual | O patamar atual é o novo normal |
| Base | Meio do caminho até a média de 20–25 anos do próprio índice | Reversão parcial |
| Conservador | Média de longo prazo do próprio índice | Reversão completa |

Regras não negociáveis:
- Crescimento real do lucro **não excede** o PIB real esperado sem justificativa escrita.
- Nunca modele `Δ(P/L)` positivo.
- Sempre em termos reais **e** nominais, com a inflação declarada.
- Confronte com pelo menos uma projeção institucional (Damodaran, Vanguard) e explique a
  diferença.

## Bloco D — Atrito

| # | Item | Onde obter | Meta |
| --- | --- | --- | --- |
| D1 | TER | Ficha | Referência, não decisão |
| D2 | **Tracking difference 3 e 5 anos** | Relatório anual ou comparadores | O número que decide |
| D3 | Domicílio do fundo | Ficha (Irlanda, Luxemburgo, EUA) | Define retenção e estate tax |
| D4 | Acumulação ou distribuição | Ficha | Acc na fase de acumulação |
| D5 | Método de replicação | Ficha | Física preferível; sintética exige avaliar contraparte |
| D6 | Patrimônio do fundo | Ficha | Abaixo de ~US$ 100 mi, risco de fechamento |
| D7 | Spread médio | Corretora | Amortizado pelo prazo de permanência |
| D8 | Custo de câmbio + IOF | Corretora | Amortizado pelo prazo |
| D9 | Empréstimo de ações | Relatório anual | Receita a favor, mas com risco de contraparte |

```
Retorno líquido esperado = retorno bruto esperado (Bloco C) − atrito total (Bloco D)
```

**Esse é o número que compara dois ETFs.** Nunca compare por TER isolado, por retorno
passado ou por dividend yield.

## Bloco E — Riscos

| # | Risco | Como medir | Guard rail sugerido |
| --- | --- | --- | --- |
| E1 | Concentração | Peso top 10, peso do maior setor | Top 10 acima de 25% = tratar como concentrado |
| E2 | País único | % em um país | Exposição a um único país exige convicção explícita |
| E3 | Valuation | CAPE contra a própria média | CAPE acima de 1,5× a média = exigir compensação |
| E4 | Cambial | Moeda do ativo vs. moeda do passivo | Decisão consciente de hedge |
| E5 | Liquidez do subjacente | Liquidez da cesta, não do ETF | Evitar cestas ilíquidas |
| E6 | Ciclicidade do lucro | Margem contra a própria história | Margem em pico = descontar o crescimento |
| E7 | Contraparte | Swap, empréstimo de ações | Preferir física, sem alavancagem |
| E8 | Sequência (fase de saque) | Horizonte até o primeiro saque | Reduzir risco conforme se aproxima |

---

## Regras de decisão

Estes são os *guard rails* que resumem tudo. Existem para impedir que uma narrativa
convincente atropele a aritmética.

1. **Amplitude antes de precisão.** Um índice amplo e barato é o padrão. Qualquer desvio
   dele precisa de justificativa escrita em termos dos três componentes de retorno.
2. **Comparar apenas retorno líquido esperado**, calculado com a mesma metodologia, na
   mesma moeda e no mesmo horizonte.
3. **Nenhuma tese pode depender de expansão de múltiplo.** Se depender, é aposta em
   sentimento.
4. **Nenhuma tese pode depender de crescimento acima do PIB nominal** sem uma fonte
   identificada (recompra líquida documentada ou expansão de margem com causa).
5. **Custo estrutural vence diferença marginal de fundamento.** Uma vantagem fiscal
   permanente de 0,20% ao ano é mais confiável que uma diferença estimada de 0,50% no
   crescimento.
6. **Diversificar geograficamente é o padrão**, não a exceção — porque a evidência de que
   ações ganham vem sobretudo de um único país vencedor.
7. **Preferir o índice mais simples** que entrega a exposição desejada. Cada regra adicional
   é um lugar a mais para o backtest ter sido otimizado.
8. **Revisar uma vez por ano.** Rebalancear por regra, não por notícia.
9. **Nunca vender por causa de valuation alto.** Valuation ajusta o **aporte marginal** e a
   **expectativa**, não a posição existente ([03](03-earnings-yield-a-ancora.md), seção 5).
10. **Escrever a tese antes de comprar.** Uma frase que diga qual componente do retorno você
    está comprando e o que a invalidaria.

---

## Ficha de avaliação (modelo)

```
ETF: ____________________   Índice: ____________________   Data: __/__/____

A. COMPOSIÇÃO
   Posições: ____   Top 10: ____%   Maior país: ____ (___%)   Maior setor: ____ (___%)

B. FUNDAMENTO
   Div yield ____%   Recompra líq ____%   E/P ____%   CAPE ____
   P/B ____   ROE ____%   Payout ____%   g LPA 10a ____%
   Consistência: E/P vs ROE÷P/B  [ ] ok  [ ] divergente

C. PROJEÇÃO (10 anos, nominal / real)
   Otimista     ____% / ____%
   Base         ____% / ____%
   Conservador  ____% / ____%
   Referência externa: ____% (fonte: __________)

D. ATRITO
   TER ____%   Tracking difference 5a ____%   Domicílio ______   [ ] Acc  [ ] Dist
   Replicação ________   Patrimônio US$ ____ mi   Spread ____%
   Atrito total: ____% a.a.

E. RETORNO LÍQUIDO ESPERADO (cenário base): ____% nominal / ____% real

F. TESE EM UMA FRASE
   ______________________________________________________________

G. O QUE INVALIDARIA ESTA TESE
   ______________________________________________________________
```

## O que este checklist deliberadamente não faz

- **Não tenta prever o próximo ano.** Nenhum item aqui tem poder preditivo abaixo de 10 anos.
- **Não seleciona por retorno passado.** Retorno passado entra apenas como insumo de
  fundamento (crescimento realizado do LPA), nunca como critério de escolha.
- **Não faz market timing.** Valuation entra na expectativa e no dimensionamento do aporte,
  não na decisão de estar ou não investido.
- **Não busca alfa.** Busca capturar o retorno do mercado com o menor atrito e ao preço
  menos desfavorável possível. É um problema de otimização, não de previsão.
