# Universo de ETFs — núcleo de 50 para escala do piloto

Lista **curada** de 50 ETFs listados nos EUA (composição via SEC N-PORT). Foco em **liquidez, diversificação geográfica e atratividade**, com **menos complexidade operacional** que a lista completa de 100.

A lista expandida (100 ETFs) ficou em `data/etf_universe_full.json` para consulta.

---

## Critérios de curadoria

**Mantidos**

- Blocos amplos essenciais (global, desenvolvidos, emergentes, Europa, Ásia, Latam).
- Países grandes ou com perfil interessante (Japão, Polônia, Índia, Brasil, etc.).
- Tilts comuns: dividendo internacional, valor/growth EAFE, small cap internacional.
- Um representante quando havia duplicata (ex.: VEA em vez de EFA + SPDW + IDEV).

**Removidos (50 ETFs da lista anterior)**

| Motivo | Exemplos removidos |
| --- | --- |
| China — mapeamento e dados mais difíceis | MCHI, FXI, ASHR, EMXC |
| Hedge de câmbio — produto diferente do índice local | DXJ, HEWJ, HEDJ |
| Fronteira / muito nicho | FM, ARGT, GXG, GREK, VNM, UAE, QAT |
| Duplicata do mesmo bloco | IXUS, SPY, EEM, IEMG, SPEM, IEUR, IPAC |
| País pequeno ou volátil | TUR, EPU, ENOR, EDEN, EIRL, ENZL, EWH, EPHE |
| Japão / Europa redundante | FLJP, SCJ, JPXN, IEUS, NORW |
| Dividendo redundante | DWX, VIGI, VIG |
| Fatores extras | IMTM, EFAV, SCZ, AVDV, FNDC |
| Global redundante | ACWI, URTH, ACWX |
| Setor / RE | GXF |

---

## Prioridade

| Prioridade | Qtd | Uso |
| --- | --- | --- |
| **P1** | 31 | Rodar primeiro (amplos + países grandes + SCHY) |
| **P2** | 19 | Segunda leva (países menores, tilts, referências) |

---

## 1. Blocos amplos e referência EUA (12)

| Prioridade | Ticker | Nome | Tema |
| --- | --- | --- | --- |
| P1 | VT | Vanguard Total World Stock ETF | Global |
| P1 | VXUS | Vanguard Total International Stock ETF | Internacional amplo |
| P1 | VEA | Vanguard FTSE Developed Markets ETF | Desenvolvidos ex-US |
| P1 | VWO | Vanguard FTSE Emerging Markets ETF | Emergentes |
| P1 | VGK | Vanguard FTSE Europe ETF | Europa |
| P1 | EZU | iShares MSCI EMU ETF | Zona euro |
| P1 | VPL | Vanguard FTSE Pacific ETF | Pacífico ex-Japão |
| P1 | AAXJ | iShares MSCI All Country Asia ex Japan ETF | Ásia ex-Japão |
| P1 | ILF | iShares Latin America 40 ETF | Latam amplo |
| P1 | VTI | Vanguard Total Stock Market ETF | EUA amplo |
| P1 | VOO | Vanguard S&P 500 ETF | EUA large cap |
| P1 | SCHD | Schwab US Dividend Equity ETF | EUA dividendo |

---

## 2. Europa por país (9)

| Prioridade | Ticker | Nome | País |
| --- | --- | --- | --- |
| P1 | EWG | iShares MSCI Germany ETF | Alemanha |
| P1 | EWU | iShares MSCI United Kingdom ETF | Reino Unido |
| P1 | EPOL | iShares MSCI Poland ETF | Polônia |
| P1 | EWQ | iShares MSCI France ETF | França |
| P1 | EWL | iShares MSCI Switzerland ETF | Suíça |
| P2 | EWI | iShares MSCI Italy ETF | Itália |
| P2 | EWP | iShares MSCI Spain ETF | Espanha |
| P2 | EWN | iShares MSCI Netherlands ETF | Holanda |
| P2 | EWD | iShares MSCI Sweden ETF | Suécia |

---

## 3. Japão, Pacífico e Ásia por país (10)

| Prioridade | Ticker | Nome | País / região |
| --- | --- | --- | --- |
| P1 | EWJ | iShares MSCI Japan ETF | Japão |
| P1 | EWA | iShares MSCI Australia ETF | Austrália |
| P1 | EWC | iShares MSCI Canada ETF | Canadá |
| P2 | EWS | iShares MSCI Singapore ETF | Singapura |
| P1 | EWY | iShares MSCI South Korea ETF | Coreia do Sul |
| P1 | EWT | iShares MSCI Taiwan ETF | Taiwan |
| P1 | INDA | iShares MSCI India ETF | Índia |
| P2 | EIDO | iShares MSCI Indonesia ETF | Indonésia |
| P2 | THD | iShares MSCI Thailand ETF | Tailândia |
| P2 | EWM | iShares MSCI Malaysia ETF | Malásia |

---

## 4. Latam, África e Oriente Médio (6)

| Prioridade | Ticker | Nome | País / região |
| --- | --- | --- | --- |
| P1 | EWZ | iShares MSCI Brazil ETF | Brasil |
| P1 | EWW | iShares MSCI Mexico ETF | México |
| P2 | ECH | iShares MSCI Chile ETF | Chile |
| P1 | EZA | iShares MSCI South Africa ETF | África do Sul |
| P1 | KSA | iShares MSCI Saudi Arabia ETF | Arábia Saudita |
| P2 | EIS | iShares MSCI Israel ETF | Israel |

---

## 5. Dividendos (4)

| Prioridade | Ticker | Nome | Tema |
| --- | --- | --- | --- |
| P1 | SCHY | Schwab International Dividend Equity ETF | Dividendo internacional |
| P1 | VYMI | Vanguard International High Dividend Yield ETF | Dividendo internacional |
| P2 | IDV | iShares International Select Dividend ETF | Dividendo internacional |
| P2 | DVYE | iShares Emerging Markets Dividend ETF | Dividendo emergentes |

---

## 6. Valor, growth e small cap internacional (4)

| Prioridade | Ticker | Nome | Tema |
| --- | --- | --- | --- |
| P1 | FNDF | Schwab Fundamental International Large Company Index ETF | Valor internacional |
| P2 | EFV | iShares MSCI EAFE Value ETF | Valor EAFE |
| P2 | EFG | iShares MSCI EAFE Growth ETF | Growth EAFE |
| P1 | VSS | Vanguard FTSE All-World ex-US Small-Cap ETF | Small cap internacional |

---

## 7. Complementos líquidos (5)

Segunda linha simples, sem China nem hedge.

| Prioridade | Ticker | Nome | Por que ficou |
| --- | --- | --- | --- |
| P2 | FEZ | SPDR EURO STOXX 50 ETF | Mega caps europeias — muito líquido |
| P2 | SCHF | Schwab International Equity ETF | Par Schwab com SCHY / FNDF |
| P2 | SCHC | Schwab International Small-Cap Equity ETF | Small cap desenvolvidos (Schwab) |
| P2 | IEFA | iShares Core MSCI EAFE ETF | Referência MSCI EAFE |
| P2 | QQQ | Invesco QQQ Trust | Referência EUA growth |

---

## 8. Resumo geográfico

| Região | ETFs na lista |
| --- | --- |
| Global / multi-região | VT, VXUS, VEA, VWO, VGK, EZU, VPL, AAXJ, ILF |
| EUA (referência) | VTI, VOO, SCHD, QQQ |
| Europa país | EWG, EWU, EPOL, EWQ, EWL, EWI, EWP, EWN, EWD, FEZ |
| Japão | EWJ |
| Pacífico / norte | EWA, EWC, EWS |
| Ásia emergente | EWY, EWT, INDA, EIDO, THD, EWM |
| Latam | EWZ, EWW, ECH (+ ILF amplo) |
| África / Médio Oriente | EZA, KSA, EIS |
| Tilts | SCHY, VYMI, IDV, DVYE, FNDF, EFV, EFG, VSS, SCHF, SCHC, IEFA |

**Sem exposição China** nesta lista — VWO ainda pode ter peso em China via índice FTSE Emerging; isso é o bloco amplo, não um ETF só de China.

---

## 9. Ordem sugerida para escalar (após SCHY)

1. **VEA** — desenvolvidos amplos (validar pipeline)
2. **EWJ** — Japão
3. **VWO** — emergentes amplos
4. **EWZ** ou **ILF** — Latam
5. **EPOL** — Polônia
6. **VYMI** — comparar tilt de dividendo
7. **VGK** — Europa regional
8. **INDA** — Índia

Depois seguir **P1** restantes e, por último, **P2**.

---

## 10. Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `data/etf_universe.json` | **50 ETFs** — lista operacional |
| `data/etf_universe_full.json` | 100 ETFs — levantamento original |
| `data/etf_universe.md` | Este documento |
