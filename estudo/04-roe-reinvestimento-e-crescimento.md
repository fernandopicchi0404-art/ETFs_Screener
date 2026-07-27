# 04 — ROE, reinvestimento e de onde vem o crescimento

## 1. O que é ROE, em primeiros princípios

```
ROE = Lucro líquido ÷ Patrimônio líquido
```

Leitura correta: **é o juro que a empresa consegue extrair do capital dos sócios**. Se o
ROE é 15%, cada R$ 100 de patrimônio produz R$ 15 de lucro por ano.

O ROE é o parâmetro que liga a decisão de reinvestir ao crescimento futuro. Sem ele, "a
empresa vai crescer" é afirmação sem lastro.

## 2. A fórmula do crescimento sustentável

Uma empresa só tem duas coisas a fazer com o lucro: distribuir ou reinvestir. Se ela
reinveste a fração `b` do lucro e consegue o mesmo ROE sobre esse capital novo:

```
g = ROE × b

onde b = 1 − payout (fração do lucro retida)
```

Exemplo: ROE de 15%, payout de 40% (`b = 0,6`) → `g = 15% × 0,6 = 9%` ao ano.

**Isto é o motor do crescimento em primeiros princípios.** Crescimento não cai do céu:
alguém precisou deixar de receber dinheiro hoje e colocar esse dinheiro para trabalhar a
uma taxa de retorno.

Da mesma equação sai o inverso, que é a pergunta útil na prática:

```
ROE implícito = g ÷ b
```

Se um índice cresce 8% ao ano retendo 50% do lucro, ele precisa de ROE de 16%. Se o ROE
observado é 10%, ou o crescimento não é sustentável, ou está vindo de outro lugar
(alavancagem, aquisições pagas com dívida, recompras).

## 3. A ponte entre ROE, P/B e retorno esperado

Três identidades que valem decorar, porque são elas que conectam tudo:

```
(1)  E/P = ROE ÷ (P/B)
(2)  P/B justo = (ROE − g) ÷ (r − g)
(3)  g = ROE × b
```

A identidade (1) é a mais útil no dia a dia e é pura álgebra:

```
E/P = (Lucro/Patrimônio) ÷ (Preço/Patrimônio) = ROE ÷ (P/B)
```

### Por que ROE alto não significa retorno alto

Aqui está a lição central deste capítulo.

| Mercado | ROE | P/B | E/P resultante |
| --- | --- | --- | --- |
| A — alta rentabilidade, caro | 20% | 5,0 | 4,0% |
| B — rentabilidade média, barato | 10% | 1,5 | 6,7% |

O mercado A é o dobro de rentável e entrega **menos lucro por real investido** do que o B,
porque você paga mais do que o dobro pelo patrimônio.

**ROE alto é característica da empresa. Retorno alto é característica do preço.** São
coisas diferentes, e confundi-las é exatamente a armadilha do crescimento que Siegel
descreve.

O que o ROE alto de fato te dá: (a) a possibilidade de crescer mais rápido para um mesmo
nível de retenção, e (b) uma margem de segurança maior contra queda de rentabilidade. Ele
justifica pagar um múltiplo maior — a pergunta é sempre **quanto maior**, e a identidade
(2) responde isso.

### Usando a identidade (2) como teste de sanidade

Se um índice negocia a P/B de 5,0 com ROE de 20% e você acha que `r = 8%`, qual crescimento
perpétuo está embutido?

```
5,0 = (0,20 − g) ÷ (0,08 − g)
0,40 − 5g = 0,20 − g
g = 5,0%
```

Cinco por cento **nominais e perpétuos**, com ROE mantido em 20% para sempre. Isso é
plausível? Talvez, se você acredita em inflação de 2,5% mais 2,5% real. É esse tipo de
pergunta que a identidade permite fazer — ela transforma "está caro" em "o preço embute X;
X é razoável?".

## 4. O limite duro: o lucro agregado não pode crescer acima do PIB para sempre

Siegel é explícito sobre isso: se os lucros corporativos crescessem indefinidamente acima
da economia, eles acabariam espremendo salários, aluguéis e toda outra forma de renda até
zero. Impossível por construção.

Então, no muito longo prazo:

```
crescimento do lucro agregado ≤ crescimento do PIB nominal
```

**Mas — e este é o ponto sutil — o lucro *por ação* pode crescer acima do PIB
indefinidamente**, desde que o número de ações caia. Siegel dá o exemplo aritmético: com
dividend yield de 2% e todo o caixa excedente usado em recompra, o número de ações cairia
2% ao ano, e o LPA cresceria 5% enquanto o lucro agregado cresce 3%.

## 5. A contestação: a diluição de 2%

Bernstein e Arnott (*Financial Analysts Journal*, 2003) atacaram exatamente esse ponto e
mostraram o oposto no dado histórico.

O achado deles, por dois métodos independentes:

- Comparando a série de dividendos de Dimson–Marsh–Staunton do século XX com o PIB, os
  dividendos cresceram, em média, **2,3 pontos percentuais mais devagar que o PIB**, mesmo
  em países que não foram destruídos por guerras.
- Medindo a diferença entre o crescimento do valor de mercado agregado e o crescimento dos
  preços das ações na base CRSP (EUA, desde 1926), aparece uma **diluição líquida de 2,3%
  ao ano** no número de ações.

A explicação em primeiros princípios é elegante:

> Boa parte do crescimento do PIB vem da **criação de empresas novas**, não do crescimento
> das empresas existentes. Quem já é acionista das empresas de hoje não captura o valor
> criado pelas empresas de amanhã — ele precisa comprá-las, emitindo capital.

E sobre recompras: o que importa não é o volume bruto de recompras, é a **recompra
líquida** (recompras menos emissões, incluindo IPOs e remuneração em ações). No século XX,
em quase todos os países, a emissão superou a recompra em 2% ao ano ou mais.

### Como conciliar Siegel e Bernstein/Arnott

Não são incompatíveis — falam de períodos e escopos diferentes:

- Siegel está certo de que **é possível** o LPA crescer acima do PIB quando as recompras
  líquidas são positivas. Isso de fato aconteceu nos EUA em boa parte das últimas três
  décadas.
- Bernstein e Arnott estão certos de que **historicamente e globalmente** a emissão líquida
  foi positiva, e que a diluição é a regra, não a exceção.

**Regra operacional que tiramos disso:** não assuma crescimento de LPA acima do PIB nominal
por padrão. Se for assumir, **prove com o número de emissão líquida do índice específico**.
E lembre que a recompra líquida americana das últimas décadas é um regime, não uma lei.

## 6. A contestação mais desconfortável: reter mais não gerou crescer mais

Arnott e Asness (*Financial Analysts Journal*, 2003) testaram diretamente a intuição
`g = ROE × b` no agregado do mercado americano. Resultado:

> **Payouts altos precederam crescimento de lucro mais rápido. Payouts baixos precederam
> crescimento mais lento.** Exatamente o contrário do previsto.

A relação é estatisticamente forte e robusta, e não é explicada por simples reversão à
média dos lucros.

Duas explicações candidatas, ambas plausíveis:

1. **Sinalização.** Gestores pagam dividendo alto quando estão confiantes de que não vão
   precisar cortá-lo. Payout baixo é pessimismo disfarçado de reinvestimento.
2. **Construção de império.** Quando sobra caixa demais, gestores financiam projetos
   ruins. Payout alto força disciplina: só os melhores projetos sobrevivem.

Siegel, aliás, reconhece o mesmo mecanismo no livro, com o nome que a academia usa —
**custos de agência**: "o pagamento de dividendos em dinheiro ou recompras comprometidas
frequentemente reduz a tentação da administração de perseguir objetivos que não maximizam
o valor do acionista".

**O que fazer com isso na prática:** `g = ROE × b` é o **teto teórico** do crescimento, não
a expectativa. Trate payout baixo com ceticismo, não com otimismo. E dê preferência a
índices onde a retenção historicamente virou lucro, não apenas balanço maior.

## 7. Cuidados ao ler ROE de um índice

O ROE é fácil de inflar contabilmente. Antes de usar o número, verifique:

1. **Alavancagem (decomposição DuPont).**
   `ROE = margem líquida × giro do ativo × alavancagem`. Um ROE de 20% obtido com
   alavancagem 4× é um animal diferente de um ROE de 20% com alavancagem 1,5×. O primeiro é
   frágil a juros e a crédito.
2. **Recompras encolhem o patrimônio líquido.** Empresa que recompra ações acima do valor
   patrimonial reduz o PL contábil e **infla o ROE mecanicamente**, sem ter ficado mais
   rentável. Em casos extremos o PL fica negativo e o ROE perde qualquer significado.
3. **Intangíveis não capitalizados.** Software, marca e P&D viram despesa em vez de ativo.
   Isso reduz o patrimônio contábil e infla o ROE de empresas de tecnologia. É uma das
   razões pelas quais o ROE agregado americano subiu tanto nas últimas décadas — parte é
   real, parte é artefato contábil.
4. **Composição setorial.** Comparar o ROE de um índice global com o de um índice de
   tecnologia é comparar coisas diferentes. Compare com a **própria história do índice**.

## 8. O que medir num ETF

| Métrica | Por que importa | Como usar |
| --- | --- | --- |
| ROE agregado do índice | Qualidade do reinvestimento | Entrada da identidade `E/P = ROE ÷ P/B` |
| P/B agregado | Preço pago pelo patrimônio | Junto com ROE, dá o E/P |
| Payout médio | Quanto está sendo retido | Teto de crescimento `g = ROE × b` |
| Crescimento histórico do LPA (10 anos) | Se a retenção virou lucro | Compare com `ROE × b` do período |
| Variação do número de ações do índice | Diluição ou recompra líquida | Some (ou subtraia) direto na projeção |
| Alavancagem agregada | Fragilidade do ROE | Ajuste a expectativa para baixo se alta |

## Resumo do capítulo

- `g = ROE × b` é o motor do crescimento — e é um **teto**, não uma previsão.
- `E/P = ROE ÷ (P/B)`: ROE alto só vira retorno alto se você não pagar por ele.
- `P/B = (ROE − g) ÷ (r − g)` permite extrair qual crescimento o preço embute.
- Lucro agregado não cresce acima do PIB para sempre; LPA pode, via recompra líquida — mas
  o histórico global mostra **diluição** de ~2% ao ano, não recompra.
- No agregado, payout alto historicamente **antecedeu** crescimento maior, não menor.
- Desconfie de ROE inflado por alavancagem, recompra ou contabilização de intangíveis.
