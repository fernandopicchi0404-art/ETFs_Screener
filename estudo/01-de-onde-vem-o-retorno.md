# 01 — De onde vem o retorno (primeiros princípios)

## 1. O que você compra quando compra uma ação

Uma ação é o **direito residual sobre o caixa que a empresa gera**. "Residual" quer dizer:
o que sobra depois de pagar fornecedores, salários, impostos e credores. Nada além disso.

Consequência direta: se a empresa nunca devolvesse nada ao acionista — nem hoje, nem daqui
a 100 anos, nem na liquidação — a ação valeria zero, por mais lucrativa que fosse no papel.
John Burr Williams colocou isso em 1938, e Siegel cita a passagem no capítulo 5 de *Stocks
for the Long Run*:

> "Lucros são apenas um meio para um fim, e o meio não deve ser confundido com o fim."

Se o lucro retido não vira caixa para o acionista lá na frente, ele é dinheiro perdido.

## 2. A conta do retorno de um período

Você compra por `P0`. Um ano depois recebe `D1` de caixa e a ação vale `P1`. O retorno é:

```
R = (D1 + P1 − P0) / P0
```

Agora o truque que abre tudo. Todo preço pode ser escrito como lucro × múltiplo:

```
P = LPA × (P/L)
```

Substituindo `P1` e `P0` por essa decomposição:

```
1 + R  =  D1/P0  +  (LPA1 / LPA0) × (P/L₁ ÷ P/L₀)
```

Ou, na forma aproximada que usamos no dia a dia (válida para taxas pequenas):

```
R  ≈  dividend yield  +  crescimento do LPA  +  variação do P/L
       └── renda ──┘   └── fundamento ────┘   └── humor ──┘
```

**Isso não é um modelo. É álgebra.** Não existe uma quarta fonte de retorno. Qualquer
história sobre por que um ETF vai render bem tem que aterrissar em um desses três termos —
ou está errada.

## 3. Os três termos, um a um

### Termo 1 — Renda (o que a empresa devolve)

É o caixa que sai da empresa e vai para o dono: **dividendos + recompras líquidas de
ações**. A recompra entra aqui porque comprar as próprias ações é economicamente idêntico
a pagar dividendo: sai caixa da empresa, e cada acionista que ficou passa a ter uma fatia
maior. O nome agregado é *shareholder yield*.

É o termo mais confiável dos três: você observa hoje, não precisa prever.

### Termo 2 — Crescimento do lucro por ação

Note bem: **por ação**, não agregado. É a distinção mais importante e mais ignorada do
tema. O lucro total da economia e o lucro por ação de quem já é acionista são coisas
diferentes, porque novas ações são emitidas o tempo todo (IPOs, follow-ons, remuneração em
ações). Isso está detalhado no arquivo [04](04-roe-reinvestimento-e-crescimento.md).

### Termo 3 — Reprecificação (mudança no múltiplo)

Quanto o mercado está disposto a pagar por R$ 1 de lucro. Bogle chama esse termo de
**"retorno especulativo"**, em contraste com os dois primeiros, que ele chama de
**"retorno de investimento"**.

Característica que define a estratégia inteira:

- Em **1 ano**, esse termo domina o retorno e é imprevisível.
- Em **30 anos**, ele tende a zero em importância (uma queda de P/L de 27,5 para 15 diluída
  em 50 anos custa cerca de −1,2% ao ano).
- Em **10 anos**, ele é grande o suficiente para decidir o resultado — e é exatamente aí
  que a maioria das decisões de alocação vive.

## 4. Por que o múltiplo é o único termo que "se paga de volta"

Existe uma assimetria que vale internalizar.

Os termos 1 e 2 são **fluxo**: cada ano entrega um pouco e o que foi entregue não volta.
O termo 3 é **estoque**: é a mudança de uma relação (preço/lucro) que tem limites
econômicos. O P/L não pode subir para sempre, porque isso significaria earnings yield
convergindo a zero — ou seja, ninguém exigindo retorno nenhum para correr risco de renda
variável.

É por isso que múltiplo alto hoje é literalmente **retorno futuro emprestado do futuro**:
se o P/L subiu de 15 para 40, boa parte do retorno dos últimos anos foi reprecificação, e
essa parcela não se repete a partir do novo patamar.

## 5. Real versus nominal

Ações são **ativos reais**: as empresas vendem bens e serviços a preços que sobem com a
inflação, e os lucros nominais acompanham. Títulos prefixados não têm essa propriedade —
a inflação corrói o cupom sem compensação.

Por isso Siegel trabalha quase sempre em termos reais, e nós também vamos. A conversão:

```
retorno nominal ≈ retorno real + inflação esperada
```

Quando você projetar um ETF, **decida em qual moeda de medida está trabalhando e não
misture.** O erro mais comum em projeção é somar um crescimento nominal de lucro com um
earnings yield e comparar o resultado com uma meta real.

## 6. Um exemplo numérico para fixar

Mercado hipotético, horizonte de 10 anos:

| Componente | Premissa | Contribuição a.a. |
| --- | --- | --- |
| Dividend yield | 1,8% | +1,8% |
| Recompra líquida | 0,7% | +0,7% |
| Crescimento real do LPA | 2,5% | +2,5% |
| Inflação | 2,5% | +2,5% |
| P/L de 25 → 20 em 10 anos | `(20/25)^(1/10) − 1` | −2,2% |
| **Retorno nominal esperado** | | **≈ 5,3%** |
| **Retorno real esperado** | | **≈ 2,7%** |

Repare no tamanho do estrago do último termo. Uma compressão de múltiplo relativamente
suave (25 → 20, um patamar ainda acima da média histórica) come **quase metade** do retorno
nominal da década. Não é preciso crise nenhuma para isso acontecer — basta o múltiplo
voltar devagar para perto do normal.

E repare no oposto: se o múltiplo ficasse parado em 25, o retorno nominal seria 7,5%. A
diferença entre "década boa" e "década medíocre" está inteira no termo que ninguém
consegue prever — mas cujo **ponto de partida** é observável hoje.

## 7. Como isso se aplica a um ETF

Um ETF de índice amplo é, por construção, a **média ponderada por valor de mercado** das
empresas do índice. Isso significa que:

- O `dividend yield` do ETF é a média ponderada dos yields das empresas.
- O `E/P` do ETF é o lucro agregado do índice dividido pelo valor de mercado agregado.
- O `crescimento do LPA` do índice é o crescimento do lucro agregado **menos a diluição
  líquida** de ações no índice.
- O `Δ(P/L)` do índice é a reprecificação do mercado inteiro.

Ou seja: **os mesmos três termos, medidos no agregado.** Avaliar um ETF é avaliar uma
empresa gigante e diversificada. Não muda nada de conceito — muda a fonte dos dados, que
passa a ser a ficha do índice em vez do balanço de uma empresa.

## Resumo do capítulo

- Retorno = renda + crescimento do LPA ± reprecificação. Não existe quarto termo.
- Renda é observável, crescimento é estimável, reprecificação é o risco.
- Múltiplo alto na entrada não é "otimismo do mercado": é subtração matemática do retorno
  futuro, a menos que o múltiplo se sustente para sempre.
- Um ETF é a mesma conta feita no agregado do índice.
