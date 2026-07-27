# 03 — Earnings yield: a âncora do retorno real

## 1. Definição

```
Earnings yield (E/P) = Lucro por ação ÷ Preço = 1 ÷ (P/L)
```

Um P/L de 25 é um earnings yield de 4%. Um P/L de 12,5 é um earnings yield de 8%.

O jeito de pensar nisso: **o earnings yield é o "juro" que a empresa gera sobre o preço que
você paga**. Se você comprasse a empresa inteira à vista e ela nunca crescesse nem
encolhesse, esse seria o seu retorno perpétuo.

## 2. Por que o E/P prevê o retorno real (a demonstração)

Muita gente trata "earnings yield ≈ retorno esperado" como regra de bolso. Não é regra de
bolso — tem uma condição precisa por trás, e vale entender qual é, porque é dela que sai o
julgamento sobre quando a regra vale.

Partindo de Gordon com reinvestimento explícito:

- `g = ROE × b`, onde `b` é a fração do lucro retida (não distribuída)
- `Preço / Patrimônio = (ROE − g) ÷ (r − g)`, onde `r` é o retorno exigido
- `E/P = ROE ÷ (P/B)` — porque `E/P = (E/PL) ÷ (P/PL)`

Juntando as três:

```
E/P = ROE × (r − g) ÷ (ROE − g)
```

Agora o resultado bonito. **Se `ROE = r`** — isto é, se a empresa reinveste exatamente ao
custo do capital próprio:

```
E/P = r × (r − g) ÷ (r − g) = r
```

**O earnings yield é exatamente igual ao retorno esperado, qualquer que seja a taxa de
crescimento.** O crescimento some da conta. Faz sentido em primeiros princípios: se o
reinvestimento rende exatamente o que o acionista exige, crescer não cria nem destrói
valor — é indiferente distribuir ou reter.

### O que acontece quando ROE ≠ r

| Situação | Relação | Leitura |
| --- | --- | --- |
| `ROE = r` | `E/P = r` | Earnings yield **é** o retorno esperado |
| `ROE > r` | `E/P < r` | Earnings yield **subestima** o retorno |
| `ROE < r` | `E/P > r` | Earnings yield **superestima** o retorno |

Exemplo do caso `ROE > r`: com `ROE = 15%`, `r = 8%`, `g = 5%`, temos
`E/P = 0,15 × 0,03 ÷ 0,10 = 4,5%` — bem abaixo dos 8% de retorno esperado.

**Consequência prática e importante:** em mercados de ROE estruturalmente alto (o caso dos
EUA hoje), o earnings yield tende a subestimar o retorno esperado — **desde que** o ROE alto
se sustente e a empresa continue conseguindo reinvestir naquela taxa. As duas condições são
grandes. Concorrência corrói ROE alto, e empresas maduras não têm onde reinvestir a esse
retorno.

Isso não é licença para pagar qualquer múltiplo. É um alerta de que a comparação de E/P
entre mercados com perfis de rentabilidade diferentes precisa de ajuste. Veja o
[arquivo 04](04-roe-reinvestimento-e-crescimento.md).

## 3. A evidência empírica de Siegel

Do capítulo 5 de *Stocks for the Long Run* (tabela 5-1, 1871–1996):

| Período | Retorno real | E/P mediano | Diferença |
| --- | --- | --- | --- |
| 1871–1996 | 6,80% | 7,30% | −0,50 p.p. |
| 1871–1945 | 6,57% | 7,35% | −0,78 p.p. |
| 1946–1996 | 7,13% | 6,96% | +0,17 p.p. |

Um século e meio de dados e a diferença fica dentro de menos de um ponto percentual. É
provavelmente a relação mais robusta de todo o material.

## 4. O problema do lucro de um ano só, e o CAPE

O E/P tem um defeito prático: o lucro de um único ano é volátil e cíclico. No fundo de uma
recessão o lucro despenca, o P/L explode, e o indicador diz "caríssimo" exatamente quando o
mercado está barato. É o inverso do que você quer.

A correção de Robert Shiller é o **CAPE** (*Cyclically Adjusted P/E*, ou Shiller P/E):

```
CAPE = Preço real do índice ÷ média dos lucros reais dos últimos 10 anos
```

Dez anos porque é aproximadamente um ciclo econômico completo. Ambos deflacionados pelo
IPC, para comparação válida entre décadas.

**Earnings yield do CAPE = 1 ÷ CAPE.** É essa a versão do earnings yield que usamos para
projeção de longo prazo.

### Onde estamos (julho/2026)

| Referência | Valor |
| --- | --- |
| CAPE do S&P 500 | **41,4** |
| E/P implícito | **2,4%** |
| Média histórica do CAPE desde 1881 | ~17,8 |
| CAPE em 12 meses antes | 37,5 |
| Mínimo recente (out/2022) | ~27 |

Só duas vezes em 145 anos o CAPE passou de 40: 1999–2000 e agora.

## 5. O que o CAPE prevê e o que não prevê

**Prevê:** retorno real médio em janelas de 10 a 20 anos. A relação inversa entre CAPE
inicial e retorno subsequente é uma das mais estáveis da literatura empírica — a correlação
costuma aparecer entre −0,7 e −0,8, com R² entre 0,4 e 0,7 dependendo do período e da
metodologia.

**Não prevê:** absolutamente nada sobre os próximos 1, 2 ou 3 anos. Um CAPE de 40 não diz
que vem crash, nem quando. Diz que o retorno *médio da década* provavelmente será abaixo da
média.

Repita isso até virar reflexo: **valuation é um indicador de retorno esperado, não um sinal
de timing.** Quem usou CAPE alto para sair do mercado em 2015 perdeu uma década de alta.

## 6. O Excess CAPE Yield: comparar com renda fixa

Shiller propôs um refinamento que resolve uma crítica legítima ("CAPE alto se justifica
quando juro está baixo"):

```
Excess CAPE Yield = (1 ÷ CAPE) − juro real de 10 anos
```

É o prêmio que a bolsa oferece **acima** do título indexado à inflação. Faz mais sentido
que o CAPE puro porque compara o retorno da bolsa com a alternativa real disponível na
mesma data.

Evidência ligada a isso: CAPEs altos se sustentam quando o juro real é profundamente
negativo, e ficam bem mais difíceis de defender quando o juro real de 10 anos passa de
1,5%–2%.

## 7. Cuidados ao usar E/P e CAPE em ETFs

Estes são os erros que estragam a análise na prática:

1. **Não compare CAPE entre índices de composição muito diferente.** Um índice pesado em
   tecnologia (ROE alto, pouco capital) merece um múltiplo maior que um índice pesado em
   bancos e commodities. Comparar CAPE de S&P 500 com CAPE de Ibovespa sem ajuste de
   composição não diz quase nada.
2. **Cuidado com mudança de composição ao longo do tempo.** O S&P 500 de 1990 e o de 2026
   são negócios diferentes. A "média histórica de 17,8" foi calculada sobre uma economia
   com muito mais indústria pesada.
3. **Cuidado com o denominador em índices pequenos ou de setor único.** Se algumas empresas
   dão prejuízo, o lucro agregado despenca e o P/L fica sem sentido. Nesses casos, prefira
   preço/vendas ou preço/patrimônio como cheque de sanidade.
4. **Lucro contábil ≠ lucro econômico.** Baixas contábeis, amortização de intangíveis e
   remuneração em ações distorcem. O CAPE suaviza parte disso, mas não tudo.
5. **Verifique se o E/P divulgado é *trailing* (12 meses passados) ou *forward*
   (projetado).** Forward é sistematicamente mais otimista, porque analistas erram para
   cima. Para projeção de longo prazo, use trailing ou CAPE.

## 8. Como usar isto na avaliação de um ETF

O procedimento mínimo:

1. Pegue o **E/P** e, se disponível, o **CAPE** do índice que o ETF replica.
2. Compare com a média histórica **do próprio índice** (não com a de outro índice).
3. Trate o E/P como o **piso do retorno real esperado** se o ROE agregado for próximo do
   custo de capital, e como possivelmente conservador se o ROE for estruturalmente alto e
   sustentável.
4. Compare o E/P com o juro real de 10 anos da mesma moeda: esse é o prêmio que você está
   sendo pago para correr risco de bolsa.
5. Se o múltiplo estiver muito acima da própria média histórica, **assuma reprecificação
   negativa na sua projeção**. Não zere o termo — zerar é uma aposta implícita de que o
   patamar atual é o novo normal.

## Resumo do capítulo

- `E/P = ROE ÷ (P/B)` e `E/P = ROE × (r − g) ÷ (ROE − g)`. Quando `ROE = r`, o earnings
  yield é exatamente o retorno esperado.
- Empiricamente, o E/P mediano bateu o retorno real de longo prazo nos EUA com erro menor
  que 1 ponto percentual em 125 anos.
- Use CAPE para longo prazo, porque o lucro de um ano é cíclico demais.
- CAPE hoje (jul/2026): 41,4 no S&P 500, contra média histórica de ~17,8.
- CAPE prevê décadas, não anos. Não é sinal de timing.
