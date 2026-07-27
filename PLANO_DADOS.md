# Organização de dados — composição e pipeline

Este documento descreve onde cada tipo de informação fica guardado e como rodar a
coleta de composição dos ETFs.

## Princípio

| Tipo | Onde fica | Frequência |
| --- | --- | --- |
| Regras e catálogo | Git (`data/catalog/`, código Python) | Quando mudamos metodologia |
| Composição bruta SEC | `data/raw/sec/` | Quando sai novo N-PORT |
| Banco organizado | `data/database/etf_screener.sqlite` | Atualizado pelos scripts |
| Exportações para leitura | `data/exports/` | Após cada extração |
| Cache ROIC (futuro) | `data/cache/` | Consultas à API |
| Runs / logs | `data/runs/` | Cada execução em lote |

O banco SQLite **não vai para o Git** — só a estrutura (`etf_screener/database/schema.sql`).

## Tabelas principais (fase 1)

- `etfs` — cadastro dos 50 ETFs do universo curado
- `assets` — empresas únicas (deduplicadas por ISIN, CUSIP ou nome+país)
- `composition_snapshots` — uma linha por data de composição de cada ETF
- `holdings` — posições e pesos de cada snapshot
- `extraction_runs` — histórico das execuções de coleta
- `prices` — reservada para atualização recorrente de preços (fase 2)

## Scripts

### 1. Sincronizar cadastro de ETFs

```bash
python3 scripts/sync_etf_registry.py
```

Lê `data/etf_universe.json` e grava os 50 ETFs em `etfs`.

### 2. Extrair composição (N-PORT)

Um ETF:

```bash
python3 scripts/update_holdings.py --etf SCHY
```

Por prioridade:

```bash
python3 scripts/update_holdings.py --priority P1
```

Todos (pode demorar — consulta a SEC):

```bash
python3 scripts/update_holdings.py --all
```

Reprocessar mesmo arquivo:

```bash
python3 scripts/update_holdings.py --etf SCHY --force
```

### 3. Conferir resultados

- Banco: `data/database/etf_screener.sqlite`
- CSV por ETF: `data/exports/compositions/{ticker}/composicao_etf.csv`
- Resumo do lote: `data/exports/compositions/extraction_summary_*.json`

## Fluxo da extração

1. Localiza o N-PORT mais recente na SEC (por CIK da gestora ou busca pelo nome).
2. Baixa o XML bruto em `data/raw/sec/{ticker}/`.
3. Extrai posições, classifica ações (EC/EP) e normaliza pesos.
4. Grava snapshot + holdings no banco.
5. Deduplica empresas em `assets` (ISIN → CUSIP → nome+país).
6. Exporta CSV para consulta.

## Limitações atuais

- ETFs sem N-PORT encontrado ficam com status `not_found` no resumo (ex.: gestoras sem
  CIK mapeado). Ajuste em `data/catalog/sec_issuer_defaults.json`.
- Gestoras com muitos fundos (iShares) usam busca por nome além do CIK.
- Fundamentos e preços ainda não são coletados nesta fase.

## Próxima fase

- `update_fundamentals.py` — demonstrativos ROIC (esporádico)
- `update_prices.py` — preços históricos (mensal/semanal)
- `calculate_etf_metrics.py` — consolidação com snapshot de avaliação
