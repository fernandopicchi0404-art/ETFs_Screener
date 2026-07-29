# Plano: composição de ETFs via gestoras + continuidade do processo

## O problema

Hoje a composição depende **só da SEC (N-PORT)**. Isso deixou de fora vários ETFs importantes — em especial **todos os Vanguard** (VT, VOO, VXUS, VEA, etc.) e alguns iShares (EWJ, EZU).

Resultado prático: poucos ETFs ativos no pipeline e buracos nos temas que você pediu (mundial, EUA, Europa, Japão, dividendos/valor, REITs).

## O que a pesquisa mostrou (jul/2026)

Testamos fontes reais neste ambiente. Resumo:

| Fonte | Como pegar | Identificadores | Frequência | Veredito |
| --- | --- | --- | --- | --- |
| **Vanguard (site)** | API JSON pública do perfil do fundo | **ISIN + CUSIP + SEDOL + ticker** + peso | ~mensal (ex.: 2026-06-30) | **Melhor caminho** para destravar Vanguard |
| **iShares / BlackRock** | CSV `.../products/{id}/{slug}/latest-holdings.csv` | ticker, nome, peso, país, bolsa — **sem ISIN** | diária | Excelente fallback quando SEC falha |
| **SPDR / State Street** | XLSX `holdings-daily-us-en-{ticker}.xlsx` | CUSIP (“Identifier”) + SEDOL + ticker | diária | Bom para SPY/FEZ; RSP precisa mapear URL certa |
| **Schwab** | Export no site da gestora | (não validado aqui — site bloqueou 403) | diária | Secundário: SEC já funciona para SCHD/SCHY |
| **SEC N-PORT** | XML trimestral (já implementado) | ISIN/CUSIP/LEI | trimestral, com atraso | Mantém como fonte oficial “regulatória” |
| **Fonte única mágica** | JustETF / Yahoo / agregadores | incompleto ou pago | — | **Não usar** como fonte principal de holdings |

### Achado crítico (já validado)

A API da Vanguard responde para **todos** os ETFs Vanguard que estavam pausados por `sem_composicao_sec`:

VT (~10k), VXUS (~8,7k), VEA, VWO, VGK, VPL, VTI, VOO (~504), VYMI, VSS, e também **VNQ / VNQI** (REITs).

Exemplo de endpoint:

`https://investor.vanguard.com/investment-products/etfs/profile/api/{ticker}/portfolio-holding/stock?start=1&count=500`

(paginado; traz ISIN — essencial para o mapeamento ROIC.)

---

## ETFs que você pediu — o que são e o que incluir

Assunção: continuamos no universo **listado nos EUA** (encaixa no pipeline atual + ROIC). Equivalentes UCITS europeus (ex.: VWCE) ficam anotados, mas fora da 1ª leva.

### 1. FTSE All World / mundial

| Ticker | Papel | Fonte composição |
| --- | --- | --- |
| **VT** | Mundial amplo (FTSE Global All Cap; ~mundo + small cap) — o mais próximo de “All World” nos EUA | Vanguard API |
| VEU | FTSE All-World **ex-US** (sem EUA) | Vanguard API |
| ACWI | MSCI ACWI (mundial, sem small cap) | SEC ou iShares CSV |
| URTH | MSCI World (só desenvolvidos, **com** EUA) | SEC ou iShares CSV |

Nota: **VWCE** (Vanguard FTSE All-World UCITS) é o equivalente europeu popular. Só entra se decidirmos abrir UCITS depois.

### 2. VOO / EUA large cap

| Ticker | Papel | Fonte |
| --- | --- | --- |
| **VOO** | S&P 500 (Vanguard) | Vanguard API |
| VTI | Mercado total EUA | Vanguard API |
| IVV / SPY | S&P 500 (iShares / SPDR) — referência | iShares CSV / SPDR XLSX |
| **RSP** | **S&P 500 Equal Weight** | SPDR (mapear download) |

### 3. MSCI World ex-USA (desenvolvidos fora dos EUA)

“MSCI World ex-USA” = desenvolvidos sem EUA (não inclui emergentes).

| Ticker | Índice | Fonte |
| --- | --- | --- |
| **IDEV** | MSCI World ex USA | SEC / iShares CSV |
| IEFA | MSCI EAFE (sem Canadá; próximo, mas não idêntico) | SEC / iShares |
| VEA | FTSE Developed ex-US (proxy barato Vanguard) | Vanguard API |
| SCHF | FTSE Developed ex-US (Schwab) | SEC |

Se a intenção for “mundo sem EUA **com** emergentes”, use **VXUS / IXUS / ACWX**, não IDEV.

### 4. Europa + países desenvolvidos

Já temos vários países (EWG, EWU, EWQ…). Completar o bloco:

| Prioridade | Tickers | Por quê |
| --- | --- | --- |
| Amplos | **VGK**, **IEUR**, EZU, FEZ | Europa / zona euro / blue chips |
| Países núcleo | EWG, EWU, EWQ, EWL, EWI, EWP, EWN, EWD | Já no catálogo |
| Opcionais | EDEN (DK), ENOR (NO), EIRL (IE), EFNL (FI) | Países menores — P3 |

### 5. Japão

| Ticker | Papel | Fonte |
| --- | --- | --- |
| **EWJ** | MSCI Japan (padrão) | iShares CSV (SEC falhou) |
| **FLJP** | FTSE Japan (barato, Franklin) | SEC / site Franklin |
| BBJP | BetaBuilders Japan (baixo custo) | site JPMorgan / SEC |
| SCJ | Japão small cap | iShares CSV |
| JPXN | JPX-Nikkei 400 (qualidade) | iShares CSV |

Evitar na 1ª leva: **DXJ / HEWJ** (com hedge de câmbio — produto diferente).

### 6. Dividendos / valor

| Tema | Tickers sugeridos | Fonte |
| --- | --- | --- |
| Div. EUA | SCHD, VYM, VIG, DGRO, HDV | Vanguard API / SEC |
| Div. internacional | **SCHY**, **VYMI**, IDV | Vanguard API / SEC |
| Div. emergentes | DVYE | SEC / iShares |
| Valor internacional | **EFV**, **FNDF**, AVDV (small value) | iShares / SEC / Avantis |

### 7. REITs

| Ticker | Papel | Fonte |
| --- | --- | --- |
| **VNQ** | REIT EUA (Vanguard) | Vanguard API |
| SCHH | REIT EUA (Schwab, barato) | SEC |
| **VNQI** | Imobiliário global **ex-US** | Vanguard API |
| IFGL | Real estate desenvolvido ex-US (iShares) | iShares CSV |
| REET | REIT global (inclui EUA) | iShares CSV |

---

## Arquitetura recomendada (como integrar)

### Princípio

**Uma composição canônica por ETF**, com fonte registrada. Ordem de tentativa:

1. **Adapter da gestora** (quando confiável e com bons identificadores)  
2. **SEC N-PORT** (quando gestora falhar ou para auditoria)  
3. Marcar `not_found` — nunca inventar pesos

Para Vanguard: gestora **primeiro** (SEC não achou).  
Para iShares com SEC ok: manter SEC; CSV da gestora como **plano B** e para datas mais frescas.  
Para EWJ/EZU: iShares CSV **primeiro**.

### Novos módulos (sem remendar o parser SEC)

```
etf_screener/holdings/
  pipeline.py              # orquestra: escolhe adapter → normaliza → grava
  adapters/
    base.py                # interface comum → list[Holding]
    sec_nport.py           # o que já existe (refatorar entrada)
    vanguard_api.py        # NOVO
    ishares_csv.py         # NOVO
    spdr_xlsx.py           # NOVO (fase 2)
  normalize.py             # pesos equity → 100%, consolidar duplicatas
```

Cada adapter devolve o mesmo `Holding` que o pipeline já usa (nome, peso, ISIN/CUSIP/ticker, país…).

### Catálogo de fontes

Arquivo novo, versionado:

`data/catalog/holdings_sources.json`

Exemplo de campos por ticker:

- `preferred_source`: `vanguard_api` | `ishares_csv` | `sec_nport` | `spdr_xlsx`
- `fallback_sources`: lista
- `issuer_product_id` / `slug` (iShares)
- `notes`

Assim você (e o script) sabem **de onde** veio cada ETF, sem hardcode espalhado.

### Banco

Em `composition_snapshots`:

- Continuar usando `accession_number` como chave única — para gestora, usar chave sintética estável, ex.: `vanguard:VOO:2026-06-30`
- Preencher `source_url` com a URL real
- (Opcional, migração leve) coluna `source_type` (`sec_nport` / `vanguard_api` / …) para filtrar no dashboard

Nada de senha/token: só HTTP público.

### Fluxo depois da composição (já existe — só reativar ETFs)

```
composição (gestora ou SEC)
  → assets / ISIN
  → resolve_asset_identities (ROIC)
  → fetch fundamentos
  → calculate_etf_metrics
  → dashboard
```

Para CSV iShares **sem ISIN**: a resolução ROIC usa ticker + bolsa/país (já previsto no pipeline de identidade). Cobertura pode ser um pouco menor que Vanguard/SEC — aceitável no fallback.

---

## Fases de execução (ordem recomendada)

### Fase A — Destravar Vanguard (maior impacto)

1. Implementar `vanguard_api.py` (paginação, stock + short-term-reserve se precisar).
2. Mapear no catálogo: VT, VXUS, VEA, VWO, VGK, VPL, VTI, VOO, VYMI, VSS, VEU, VNQ, VNQI.
3. Rodar só esses tickers → gravar snapshots → exportar CSV.
4. Reativar no `etf_universe.json` (`status: active`, limpar `pause_reason`).
5. Seguir identidade → fundamentos → métricas nos P1 reativados.

**Por quê primeiro:** um adapter só libera ~10–13 ETFs centrais que hoje estão pausados.

### Fase B — iShares onde a SEC falhou + gaps

1. Implementar `ishares_csv.py` + tabela `product_id`/`slug` por ticker.
2. Prioridade: **EWJ**, **EZU**, e qualquer active ainda sem snapshot (EFV, FEZ, QQQ se necessário).
3. Reativar EWJ/EZU; rodar identidade/fundamentos.

### Fase C — Expandir o universo (os temas que faltam)

Atualizar `etf_universe.json` (e docs) com a leva abaixo, sem inflar demais:

| Tema | Incluir agora |
| --- | --- |
| Mundial / All World | VT (já), VEU |
| EUA | VOO, VTI (já), **RSP** |
| World ex-USA | **IDEV**, VEA/SCHF (já) |
| Europa ampla | VGK, IEUR, EZU |
| Japão extra | EWJ, FLJP, SCJ (BBJP se adapter ok) |
| Div / valor | VYMI, EFV, FNDF, VYM (opcional) |
| REITs | **VNQ**, **VNQI**, SCHH, IFGL |

Manter China/fronteira/hedge fora, como na curadoria atual — a menos que você peça o contrário.

### Fase D — SPDR / Invesco / Schwab (reforço)

- SPDR XLSX para FEZ, SPY, RSP.
- Invesco para QQQ se SEC continuar falhando.
- Schwab: só se SEC falhar (hoje não é o gargalo).

### Fase E — Continuidade operacional

1. `update_holdings.py` ganha `--source auto|vanguard|ishares|sec`.
2. Relatório de cobertura: quantos ETFs com snapshot fresco, % peso com ISIN, % com identidade ROIC.
3. Atualizar `COMO_USAR.md` / `PLANO_DADOS.md` / `etf_universe.md`.
4. Meta prática: **≥ 40 ETFs com composição utilizável**, depois métricas consolidadas nos P1/P2 reativados.

---

## O que não fazer

- Não depender de agregador pago/opaco como única fonte.
- Não misturar UCITS e EUA no mesmo ranking sem marcar domicílio (imposto/estrutura diferentes).
- Não tratar DXJ/HEWJ como “Japão puro”.
- Não abandonar a SEC: ela continua útil para auditoria e para gestoras sem CSV bom.
- Não instalar biblioteca nova sem necessidade: Vanguard = JSON stdlib; iShares = CSV stdlib; SPDR XLSX pode precisar de parser mínimo depois.

---

## Riscos (em linguagem simples)

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Site da gestora muda URL | Extração quebra | Catálogo central + teste automatizado por adapter |
| iShares CSV sem ISIN | Mais trabalho no mapeamento ROIC | Preferir Vanguard/SEC quando houver ISIN |
| Composição gestora ≠ N-PORT do mesmo dia | Pesos levemente diferentes | Registrar fonte e data; não misturar no mesmo snapshot |
| Bloqueio HTTP (Schwab 403) | Adapter inutilizável daqui | Usar SEC; ou baixar manual pontual se um dia precisar |

---

## Decisão recomendada (próximo passo de código)

Começar pela **Fase A (Vanguard API)** — é a forma mais limpa de recuperar quantidade e qualidade (ISIN) nos ETFs que mais faltam (VT, VOO, VXUS, etc.), e encaixa no processo atual sem gambiarra.

Depois: **Fase B (iShares CSV)** para EWJ/EZU e **Fase C** para RSP, IDEV, REITs e o reforço de dividendos/valor/Japão.
