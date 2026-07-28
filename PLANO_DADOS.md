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

## Identificação confiável dos ativos antes da ROIC

O levantamento fundamentalista só pode começar depois que cada ativo tiver um
identificador ROIC validado. Busca livre por nome não será considerada confirmação.

### O que a SEC fornece

O N-PORT pode fornecer:

- ISIN;
- CUSIP;
- LEI da empresa;
- nome e título do ativo;
- país;
- ticker em uma minoria dos registros;
- identificadores internos da gestora.

O ticker sozinho não é suficiente: `A`, por exemplo, pode existir em bolsas diferentes.
Para ser confiável, ele precisa estar ligado à bolsa ou ao MIC (código internacional da
bolsa). O ISIN será o identificador principal porque representa uma classe específica da
ação e a ROIC permite busca direta por ISIN.

### Correção obrigatória antes de nova coleta

No XML N-PORT, o ISIN aparece como atributo (`<isin value="..."/>`). O parser atual procura
o texto interno da tag e, por isso, não está preservando esse valor. Antes de retomar a
ROIC, será necessário:

1. corrigir a leitura do atributo `value`;
2. armazenar ISIN, CUSIP, LEI, ticker e outros identificadores separadamente;
3. reprocessar os XMLs já baixados;
4. reconstruir o cadastro único de ativos;
5. invalidar os mapeamentos automáticos não validados da rodada exploratória.

### Ordem de resolução na ROIC

O processo usará uma hierarquia conservadora:

1. **ISIN exato** — consultar `/tickers/search` com `search_by=isin` e aceitar somente se o
   ISIN devolvido for exatamente igual.
2. **CUSIP exato** — usar `search_by=cusip` e exigir igualdade, principalmente para EUA e
   Canadá.
3. **Ticker + bolsa/MIC** — usar somente quando os dois forem conhecidos; exigir símbolo
   qualificado exato (ex.: `NASDAQ:AAPL`).
4. **Mapeamento já aprovado** — reutilizar um identificador ROIC validado anteriormente
   para a mesma classe de ação.
5. **Nome + país** — último recurso; gera candidato para revisão, nunca aprovação
   automática quando houver dúvida.

LEI e identificadores internos serão guardados para auditoria e possível integração
futura, mas a busca atual da ROIC não oferece filtro por LEI.

### Validação obrigatória do candidato

Antes de buscar DRE, balanço, caixa ou preço, o candidato da ROIC deverá passar por:

- ISIN ou CUSIP idêntico, quando disponível;
- país da listagem compatível;
- tipo `stock` e classe ordinária/preferencial esperada;
- status listado;
- nome compatível;
- bolsa/MIC compatível, quando conhecido;
- preferência pela listagem primária;
- rejeição automática de resultado `ambiguous`.

Se os dois melhores candidatos tiverem pontuação próxima, o ativo será enviado para
revisão. O sistema não escolherá um deles por tentativa.

### Status do mapeamento

| Status | Significado | Pode coletar fundamentos? |
| --- | --- | --- |
| `verified_isin` | ISIN exato confirmado | Sim |
| `verified_cusip` | CUSIP exato confirmado | Sim |
| `verified_symbol` | ticker + bolsa confirmados | Sim |
| `manual_approved` | revisão humana documentada | Sim |
| `review_required` | candidato plausível, mas sem prova suficiente | Não |
| `not_found` | nenhum candidato confiável | Não |
| `rejected` | candidato incompatível | Não |

Cada aprovação guardará método, identificadores comparados, data, resposta da ROIC e
versão da regra. O mapeamento será global por ativo, não por ETF, para ser reaproveitado.

### Processo em duas filas

1. **Fila de identidade:** resolve e valida todos os identificadores, começando pelos
   ativos de maior peso e pelos que aparecem em mais ETFs.
2. **Fila financeira:** recebe apenas ativos com status aprovado e coleta os quatro
   conjuntos de dados financeiros.

Essa separação evita gastar chamadas com tickers errados e permite revisar todas as
ambiguidades antes da execução longa.

### Eficiência esperada

- uma busca exata por ISIN substitui várias tentativas por nome;
- respostas de identidade serão armazenadas em cache;
- empresas repetidas entre ETFs serão resolvidas uma vez;
- erros técnicos terão retry; erros de identidade não serão repetidos automaticamente;
- a fila será retomável e mostrará cobertura por peso, não apenas quantidade de empresas.

### Checagem posterior

Mesmo após o match, os dados coletados terão uma segunda validação:

- perfil da empresa coerente com nome, país e setor;
- moeda financeira e moeda de negociação plausíveis;
- período fiscal disponível;
- preço associado à classe correta;
- detecção de ADR, preferencial ou listagem secundária inesperada.

Um ativo que falhar nessa etapa volta para `review_required` e não entra no consolidado.

## Próxima fase

- corrigir e reprocessar os identificadores do N-PORT;
- `resolve_asset_identities.py` — match exato e fila de revisão;
- `update_fundamentals.py` — demonstrativos ROIC apenas para ativos aprovados;
- `update_prices.py` — preços históricos (mensal/semanal)
- `calculate_etf_metrics.py` — consolidação com snapshot de avaliação
