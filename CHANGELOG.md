# Changelog

Registro das mudanças relevantes do repositório.

## [Não publicado]

### Adicionado

- **Base de estudo sobre fundamentos de avaliação de ETFs** (pasta `estudo/`), em 12
  arquivos, partindo de *Stocks for the Long Run* (Siegel) e complementada por Bogle,
  Buffett, Damodaran, Shiller, Arnott/Asness e Dimson–Marsh–Staunton:
  - `00` — Mapa e tese central
  - `01` — De onde vem o retorno (dedução em primeiros princípios)
  - `02` — O que *Stocks for the Long Run* mostra, e as críticas ao livro
  - `03` — Earnings yield como âncora do retorno real, e o CAPE
  - `04` — ROE, reinvestimento e crescimento sustentável
  - `05` — Dividendos e recompras
  - `06` — Modelos de projeção (Bogle, Grinold-Kroner, TIR implícita, CAPE)
  - `07` — Diversificação e por que investir de forma passiva
  - `08` — Custos, impostos e mecânica do ETF
  - `09` — Checklist operacional de avaliação de ETF
  - `10` — Armadilhas e limites do método
  - `11` — Glossário e referências
- **Piloto SCHY**: pipeline para extrair composição via SEC N-PORT, mapear empresas na
  ROIC.ai, calcular métricas por ativo e consolidar ROE, earnings yield, dividend yield e
  shareholder yield.
- `PLANO_PROJETO.md`, `FORMATOS_SAIDA.md` e `COMO_USAR.md` com instruções de estudo e de
  execução do piloto.

### Corrigido

- Mapeamentos manuais ambíguos do SCHY (BOC Hong Kong, Imperial Brands, Kone, Tung Ho,
  Saudi Telecom, Schroders, Kuehne+Nagel, TMBThanachart, Gjensidige).
- Retries para timeout de rede na API ROIC; mapeamento continua após erro por ativo.
- Extração de patrimônio anterior quando a ROIC retorna apenas um exercício.
- Leitura do peso do N-PORT (`pctVal` já vem em percentual).
- Normalização de moedas/subunidades (GBX, ZAC, KWF) antes de calcular yields.
- Bloqueio de métricas com moeda incompatível ou valores implausíveis.
- Processamento por peso até atingir 90% de cobertura limpa.
- **30 tickers SCHY corrigidos** (prefixos ROIC errados e empresas mapeadas para ticker
  errado): Roche, Vinci, Michelin, Swisscom, Ahold, Kuehne+Nagel, Generali, Quebecor,
  Telekom Malaysia, Coca-Cola Femsa, Chipbond, Telstra, AXA, Scotiabank, Endesa, Manulife,
  PTT E&P, Sun Life, Naturgy, Bidvest, Central Pattana, Chicony, Spark NZ, Ooredoo,
  Great-West Lifeco, iA Financial, Hyundai Motor, KPN, TIM e Engie Brasil.
- Validação de nome relaxada para equivalentes legais (Koninklijke/Royal) e siglas
  distintivas (KPN, TIM).

### Notas

- Dados de mercado citados no material de estudo são de julho de 2026 e estão consolidados
  numa tabela ao final de `estudo/11-glossario-e-referencias.md`.
- O piloto SCHY usa dados anuais da ROIC.ai (plano gratuito: ~5 requisições/minuto).
