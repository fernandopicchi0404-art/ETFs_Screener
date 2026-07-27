# 08 — Custos, impostos e mecânica do ETF

Os capítulos anteriores estimam o retorno **do índice**. Este capítulo trata do que se perde
entre o índice e a sua conta. Em ETFs baratos, essa perda é pequena — mas ela é **certa**,
enquanto todo o resto é incerto. Por isso ela merece o mesmo rigor da projeção.

---

## 1. Taxa de administração não é o custo total

O **TER** (*Total Expense Ratio*, ou taxa de administração total) é o número que aparece na
propaganda. Ele captura a taxa do gestor, custódia e administração. Ele **não** captura:

- Custos de transação do fundo ao rebalancear o índice
- Imposto retido sobre dividendos no nível do fundo
- Receita de empréstimo de ações (que joga a favor)
- Diferença entre o preço que você paga e o valor patrimonial da cota
- Spread de compra e venda
- Custo de câmbio e IOF

A medida honesta é a **diferença de acompanhamento** (*tracking difference*):

```
Tracking difference = retorno do ETF − retorno do índice (mesmo período, mesma moeda)
```

É um número **realizado**, não estimado, e resume tudo de uma vez. É frequente um ETF com
TER de 0,07% ter tracking difference de −0,15% (custos escondidos) e outro com TER de 0,20%
ter tracking difference de −0,10% (compensado por empréstimo de ações e eficiência fiscal).

**Regra:** compare ETFs por tracking difference de 3 e 5 anos, não por TER.

Não confunda com **tracking error**, que é a *volatilidade* dessa diferença — mede
consistência, não custo.

## 2. Como o ETF replica o índice

| Método | Como funciona | Riscos |
| --- | --- | --- |
| **Física completa** | Compra todos os papéis do índice, nos pesos exatos | Custo de transação alto em índices grandes ou ilíquidos |
| **Física por amostragem** | Compra um subconjunto representativo | Desvio em relação ao índice quando a amostra falha |
| **Sintética (swap)** | Contrata um banco que entrega o retorno do índice | **Risco de contraparte** — se o banco quebra, você depende da garantia |

A replicação sintética às vezes tem vantagem fiscal (certos swaps sobre índices americanos
não sofrem retenção sobre dividendos). Para uma estratégia de longuíssimo prazo, a
simplicidade e transparência da réplica física costumam compensar a diferença.

## 3. O imposto sobre dividendos: o custo que quase ninguém soma

Este é, para um investidor brasileiro, frequentemente **maior que a taxa de administração**.

### O problema

O Brasil não tem acordo de bitributação em vigor com os EUA. Um brasileiro que detém
diretamente um ETF domiciliado nos EUA sofre **retenção de 30%** sobre os dividendos.

A Irlanda tem acordo com os EUA. Um ETF UCITS irlandês sofre **15%** de retenção sobre
dividendos de ações americanas, no nível do fundo — e as distribuições do fundo irlandês
para o investidor não-residente geralmente não sofrem retenção adicional.

### O tamanho do efeito

Sobre um dividend yield de 1,3%, a diferença de 15 pontos percentuais de retenção vale
cerca de **0,20% ao ano**. Parece pequeno. Ao longo de 30 anos, com capitalização, é uma
diferença de aproximadamente 6% no patrimônio final — provavelmente mais do que a diferença
de TER entre os dois ETFs.

Em ativos de yield mais alto (dividendos, REITs, high yield), o efeito é bem maior.

### O estate tax americano

Este é o risco mais subestimado do tema. Ativos de *situs* americano — ações americanas e
ETFs domiciliados nos EUA — acima de aproximadamente **US$ 60 mil** ficam sujeitos ao
imposto sucessório americano no falecimento de um investidor não-residente, com alíquotas
que chegam a **40%**.

ETFs irlandeses não são ativos de situs americano e ficam fora desse imposto.

### Comparativo

| Critério | ETF domiciliado nos EUA | ETF UCITS irlandês |
| --- | --- | --- |
| Retenção sobre dividendos de ações americanas | 30% na fonte | 15% no nível do fundo |
| Estate tax americano | Até 40% acima de ~US$ 60 mil | Não se aplica |
| Versão acumulação | Rara (estrutura RIC obriga distribuir) | Comum |
| Momento do imposto no Brasil | Dividendo recebido é fato gerador anual | Acc difere até a venda (Lei 14.754/2023) |
| Variedade de produtos | Muito maior | Menor, mas cobre o essencial |
| Liquidez e spread | Geralmente melhores | Geralmente piores |

**Conclusão prática:** para acumulação de longo prazo em exposição a ações americanas ou
globais, a estrutura UCITS irlandesa de acumulação tende a ser estruturalmente superior para
o brasileiro. Isso não é dica de produto — é a consequência aritmética das duas alíquotas e
do diferimento.

*Regras tributárias mudam. Confirme a situação vigente e consulte um contador antes de
decidir. As referências aqui são de julho de 2026.*

## 4. Acumulação (Acc) versus distribuição (Dist)

| | Acumulação | Distribuição |
| --- | --- | --- |
| Dividendos | Reinvestidos dentro do fundo | Pagos na sua conta |
| Imposto no Brasil | Diferido até a venda | Incide no recebimento |
| Atrito operacional | Nenhum | Você precisa reinvestir manualmente |
| Serve para | Fase de acumulação | Fase de consumo do patrimônio |

Na fase de acumulação, a versão Acc ganha por dois motivos: **diferimento fiscal** (o
imposto que você não pagou continua rendendo) e **eliminação do erro humano** de não
reinvestir. O efeito do reinvestimento é justamente o motor que Siegel documenta no
[arquivo 05](05-dividendos-e-recompras.md).

## 5. Liquidez: onde a intuição erra

A intuição diz "compre o ETF de maior volume". Está incompleto.

Um ETF tem **duas camadas de liquidez**:

1. **Liquidez na bolsa** — o volume negociado das cotas, que define o spread visível.
2. **Liquidez dos ativos subjacentes** — porque o mecanismo de criação e resgate permite
   que participantes autorizados criem cotas novas entregando a cesta de ações. Se as ações
   subjacentes são líquidas, o ETF é líquido mesmo com pouco volume próprio.

Consequência: um ETF pequeno sobre o S&P 500 é essencialmente tão líquido quanto um grande.
Já um ETF grande sobre small caps de fronteira pode ser ilíquido de verdade, porque a cesta
subjacente é ilíquida.

**O que de fato olhar:**
- **Spread** de compra e venda em condições normais (e o que acontece em dias de estresse)
- **Prêmio ou desconto** em relação ao valor patrimonial — persistente é sinal de problema
- **Patrimônio do fundo**: abaixo de aproximadamente US$ 100 milhões, cresce o risco de
  fechamento, que força realização de ganho e evento tributário no pior momento

## 6. O índice é o produto

Dois ETFs com o mesmo nome de categoria podem comprar coisas bem diferentes. O que
determina o que você tem é a **metodologia do índice**, não o marketing do ETF.

Perguntas a fazer sobre o índice:

1. **Universo.** Quais empresas podem entrar? Quantas de fato entram?
2. **Ponderação.** Valor de mercado, igual peso, fundamentos, dividendos? A ponderação por
   valor de mercado tem a propriedade valiosa de ser autoajustável (não gera giro por
   variação de preço) — as demais geram giro e custo.
3. **Concentração e capping.** Qual o peso das 10 maiores? Há teto por posição? Um índice
   "amplo" com 35% nas dez maiores não é tão amplo.
4. **Rebalanceamento.** Com que frequência? Rebalanceamento frequente é custo escondido; e
   índices previsíveis sofrem *front-running* de quem antecipa a entrada e saída de papéis.
5. **Regras de inclusão e exclusão.** Filtros de liquidez, de free float, de lucratividade.
6. **Histórico real versus simulado.** Índices novos publicam *backtest*. Backtest é
   histórico escolhido depois do fato. Trate com o ceticismo que merece.

## 7. Câmbio

Para um investidor em reais comprando ETF em dólar ou euro, o câmbio é um componente de
retorno tão grande quanto qualquer outro — e uma fonte de custo:

- **IOF** na remessa de recursos
- **Spread cambial** da corretora ou banco (frequentemente maior que o IOF)
- **Volatilidade cambial**, que no curto prazo domina o retorno em reais

Sobre hedge cambial: para exposição de longo prazo a ações globais, a maioria dos
investidores em moeda fraca não faz hedge — a exposição ao dólar funciona como proteção
contra crises domésticas, exatamente quando você mais precisa. Mas o hedge tem custo
(diferencial de juros), e a decisão deve ser consciente, não default.

## 8. Somando o atrito total

O número que entra na linha "M" da planilha do [arquivo 06](06-modelos-de-projecao.md):

```
Atrito total anual ≈ tracking difference
                   + (dividend yield × retenção incremental de imposto)
                   + spread amortizado pelo prazo de permanência
                   + custo de câmbio amortizado
```

Exemplo ilustrativo de um ETF global UCITS acumulação:

| Componente | Estimativa |
| --- | --- |
| Tracking difference | 0,12% |
| Retenção incremental (já dentro do TD) | — |
| Spread (0,05% ÷ 20 anos de permanência) | 0,003% |
| Câmbio (1,5% na entrada ÷ 20 anos) | 0,075% |
| **Atrito total** | **≈ 0,20% ao ano** |

Compare com um retorno real esperado de 2% a 4% ao ano e você vê que o atrito é da ordem de
**5% a 10% do retorno esperado**. Não é desprezível, e é a parte que você controla.

## Resumo do capítulo

- Compare por **tracking difference**, não por TER.
- Para brasileiro, o **domicílio do fundo** costuma valer mais que a taxa: 15% versus 30%
  de retenção sobre dividendos, e o estate tax de até 40% acima de US$ 60 mil.
- **Acumulação** difere imposto e elimina o erro de não reinvestir.
- Liquidez do ETF é a liquidez da **cesta subjacente**, não só o volume das cotas.
- O produto é o **índice**, não o ETF. Leia a metodologia: ponderação, concentração,
  rebalanceamento.
- Some o atrito total e subtraia da projeção. É o único número certo da conta inteira.
