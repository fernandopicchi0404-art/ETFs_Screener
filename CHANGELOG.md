# Changelog

Registro das mudanças relevantes do repositório.

## [Não publicado]

### Adicionado

- **Cobertura por peso (meta 90%)** na fila de identidade/fundamentos:
  - `etf_screener/holdings/coverage.py` seleciona só os maiores holdings até a meta.
  - Scripts `resolve_asset_identities.py` e `fetch_p1_assets.py` aceitam
    `--coverage-target` (padrão 0.90) e `--etf`.
- **Semeadura por ISIN** (`scripts/seed_identities_from_db.py`) a partir do SQLite do
  dashboard, para reaproveitar identidades/fundamentos já resolvidos sem gastar cota ROIC.
- **Adapter Vanguard API** para composição de holdings:
  - `etf_screener/holdings/vanguard_api.py` baixa posições com ISIN/CUSIP/SEDOL.
  - Pipeline escolhe fonte via `holdings_sources.json` (Vanguard → SEC).
  - Script `update_holdings.py` aceita `--source` e `--include-paused`.
  - Reativados 10 ETFs Vanguard que estavam pausados por falta de N-PORT
    (VT, VXUS, VEA, VWO, VGK, VPL, VTI, VOO, VYMI, VSS).
- **Adapter iShares CSV** (`latest-holdings.csv`) para EWJ e EZU:
  - `etf_screener/holdings/ishares_csv.py` com product_id/slug no catálogo.
  - Reativados EWJ e EZU (antes `sem_composicao_sec`).
- **Plano de extração de composições via gestoras** (`PLANO_EXTRACAO_COMPOSICOES.md`):
  pesquisa de fontes (Vanguard API, iShares CSV, SPDR XLSX), mapeamento dos temas
  pedidos (All World, VOO, World ex-USA, Europa, Japão, dividendos/valor, REITs) e
  fases A–E para integrar no pipeline sem abandonar a SEC.
- **Catálogo de fontes** (`data/catalog/holdings_sources.json`) com fonte preferencial
  por ticker e candidatos de expansão por tema.
- **Painel web (prova de conceito)** com API REST e front-end Next.js:
  - Tabelas `asset_fundamentals` e `etf_consolidated_metrics` no SQLite.
  - Scripts `seed_schy_pilot.py`, `calculate_etf_metrics.py` e `run_api.py`.
  - API integrada ao Next.js (`frontend/app/api/`) para deploy na Vercel.
  - Banco SQLite embutido em `frontend/data/` para publicação sem servidor próprio.
  - Front-end em `frontend/` com resumo de ETFs, detalhe do ETF e lista de ativos.
  - Dependências em `requirements.txt` (FastAPI, Uvicorn) para uso local opcional.
- **Pipeline de identidade confiável** antes da ROIC:
  - Correção de leitura de ISIN/ticker no N-PORT (`nport_identifiers`, `sec_nport`).
  - Resolução por ISIN → CUSIP → ticker+bolsa com validação (`identity_resolver`).
  - Tabela `asset_identities` e scripts `reprocess_compositions.py`,
    `resolve_asset_identities.py`, `run_p1_pipeline.py`.
  - Fundamentos só para ativos verificados (`fetch_p1_assets.py`).
- **Plano de identificação confiável dos ativos** em `PLANO_DADOS.md`: prioridade para
  ISIN/CUSIP exatos, ticker apenas com bolsa, validação obrigatória e fila de revisão
  separada da coleta financeira.
- **Levantamento ROIC por prioridade** (`scripts/fetch_p1_assets.py`):
  - Processa ativos únicos do P1 (ou outra prioridade) com limite de tempo.
  - Grava status em `asset_fundamental_fetches` e export parcial JSONL.
  - Respeita throttle configurável via `ROIC_REQUESTS_PER_MINUTE` no `.env` (padrão: 300).
- **Teste de taxa ROIC** (`scripts/test_roic_rate_limit.py`): valida req/min antes do lote.
- **Mapeamento ticker SEC → bolsa ROIC** (`exchange_map`) e nomes oficiais da ROIC após verificação.
- **Pipeline de composição de ETFs** (fase 1 do plano de dados):
  - Banco SQLite (`etf_screener/database/`) com ETFs, ativos, snapshots, holdings e
    tabela `prices` reservada para fase 2.
  - Catálogo em `data/catalog/` (`methodology.json`, `sec_issuer_defaults.json`).
  - Descoberta e download SEC N-PORT (`sec_discovery`, `sec_fetch`, `nport_metadata`).
  - Deduplicação de ativos por ISIN/CUSIP/nome (`asset_registry`).
  - Scripts `sync_etf_registry.py` e `update_holdings.py`.
  - Documentação em `PLANO_DADOS.md`.
- **Universo de ETFs para escala do piloto** (`data/etf_universe.md`, `data/etf_universe.json`,
  `data/etf_universe_full.json`): núcleo curado de **50 ETFs** (sem China, hedges e nichos
  complexos); lista expandida de 100 mantida como referência.
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

- Erros de fetch ROIC para tickers mexicanos com `/` na URL (codificação do símbolo).
- Preço ROIC opcional quando demonstrativos existem (recupera ROE sem earnings yield).
- Exclusões de identidade por validação rígida de país da SEC (confiança no ISIN).

### Adicionado (métricas)

- `scripts/sync_fundamentals_db.py` — popula `asset_fundamentals` a partir dos fetches OK.
- `calculate_etf_metrics.py --priority P1` — calcula agregados em lote.
- Export em `data/exports/etf_metrics/p1_consolidated.json`.
- Campo `status` no universo de ETFs (`active` / `paused`); sync respeita pausa.

### Alterado

- **21 ETFs pausados** no universo P1 (sem composição SEC ou cobertura < 90%).
  P1 ativo reduzido para **10 ETFs**: EWG, EWQ, EWT, EWW, EWY, EWZ, EZA, KSA, SCHD, SCHY.

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
  Telekom Malaysia, Coca-Cola Femsa, Chipbond, Telstra, AXA (`EURONEXT:CS`), Scotiabank,
  Endesa, Manulife, PTT E&P, Sun Life, Naturgy, Bidvest, Central Pattana, Chicony, Spark NZ,
  Ooredoo, Great-West Lifeco, iA Financial, Hyundai Motor, KPN, TIM e Engie Brasil.
- Validação de nome relaxada para equivalentes legais (Koninklijke/Royal) e siglas
  distintivas (KPN, TIM).

### Notas

- Dados de mercado citados no material de estudo são de julho de 2026 e estão consolidados
  numa tabela ao final de `estudo/11-glossario-e-referencias.md`.
- O piloto SCHY usa dados anuais da ROIC.ai (plano gratuito: ~5 requisições/minuto).
