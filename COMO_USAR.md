# Como usar este repositório

## O que tem aqui

Uma base de estudo, em português, sobre **como avaliar ETFs a partir de fundamentos** —
partindo de *Stocks for the Long Run* (Jeremy Siegel) e complementada por Bogle, Buffett,
Damodaran, Shiller, Arnott/Asness e a base histórica de Dimson–Marsh–Staunton.

O objetivo é ter um conjunto explícito de princípios para escolher veículos passivos, sem
stock picking e sem tentar adivinhar o próximo ano.

Tudo está na pasta [`estudo/`](estudo/), em arquivos numerados na ordem de leitura.

## Por onde começar

**Comece por [`estudo/00-mapa-e-tese-central.md`](estudo/00-mapa-e-tese-central.md).** Ele
tem a tese em cinco linhas, a equação central e o mapa dos outros arquivos.

Três caminhos, dependendo do seu tempo:

| Situação | Leia |
| --- | --- |
| Tenho 20 minutos | `00` → `01` → `09` |
| Quero entender de verdade | `01` até `10`, na ordem |
| Vou avaliar um ETF agora | `09` (checklist), consultando `06` e `08` |

## Como ler os arquivos

São arquivos Markdown (`.md`) — texto simples com formatação. Você pode:

- **Ler direto no GitHub**, que renderiza tudo formatado (é o jeito mais fácil).
- **Abrir em qualquer editor de texto**, se preferir ler offline.
- **Converter para PDF**, se quiser imprimir (veja abaixo).

## Gerar um PDF (opcional)

Se quiser um documento único para imprimir ou ler no tablet, com o
[Pandoc](https://pandoc.org) instalado:

```bash
pandoc estudo/*.md -o fundamentos-etfs.pdf --toc --pdf-engine=xelatex -V geometry:margin=2.5cm
```

Isso junta todos os arquivos na ordem numérica, com sumário. Não é necessário para usar o
material — é conveniência.

## Usando o checklist na prática

O arquivo [`estudo/09-checklist-de-avaliacao-de-etf.md`](estudo/09-checklist-de-avaliacao-de-etf.md)
é o operacional. Ele tem:

- **Blocos A a E** — o que coletar sobre cada ETF e onde encontrar
- **Regras de decisão** — os limites que impedem uma boa narrativa de atropelar a
  aritmética
- **Ficha de avaliação** — um modelo em branco para preencher por ETF

O fluxo é sempre:

```
1. O que o ETF possui        (Bloco A)
2. Fundamento e preço        (Bloco B)
3. Projeção de retorno       (Bloco C, usando o arquivo 06)
4. Atrito até o meu bolso    (Bloco D, usando o arquivo 08)
5. Riscos e guard rails      (Bloco E)
```

O número que compara dois ETFs é sempre o **retorno líquido esperado** (passo 3 menos passo
4), nunca a taxa de administração isolada nem o retorno passado.

## Sobre os números citados

Os dados de mercado no material são de **julho de 2026** e estão listados no final de
[`estudo/11-glossario-e-referencias.md`](estudo/11-glossario-e-referencias.md).

**Números de mercado envelhecem; fórmulas não.** Antes de usar o material para uma decisão,
atualize CAPE, earnings yield, prêmio de risco e projeções institucionais. As identidades
algébricas dos arquivos 01, 03, 04 e 06 continuam valendo.

## O que este material não é

- **Não é recomendação de investimento.** É estudo.
- **Não prevê o próximo ano.** Nada aqui tem poder preditivo abaixo de 10 anos.
- **Não busca bater o mercado.** Busca capturar o retorno do mercado com o menor atrito
  possível e ao preço menos desfavorável possível.
- **Não trata de tributação individual.** As referências fiscais do arquivo 08 são
  informativas e mudam. Confirme com um contador.

## Manutenção

- Mudanças relevantes ficam registradas em [`CHANGELOG.md`](CHANGELOG.md).
- Se algum conteúdo mudar de forma que afete como você usa o material, este arquivo é
  atualizado junto.
