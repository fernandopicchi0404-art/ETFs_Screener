# Como usar este repositório

## O que tem aqui

Duas partes complementares:

1. **Material de estudo** (`estudo/`) — fundamentos para avaliar ETFs em português, sem stock
   picking, com foco em veículos passivos.
2. **Piloto automatizado SCHY** — extrai a composição do ETF, consulta fundamentos na
   ROIC.ai e calcula métricas agregadas (ROE, earnings yield, dividend yield e shareholder
   yield).

---

## Parte 1 — Material de estudo

### Por onde começar

**Comece por [`estudo/00-mapa-e-tese-central.md`](estudo/00-mapa-e-tese-central.md).** Ele
tem a tese em cinco linhas, a equação central e o mapa dos outros arquivos.

| Situação | Leia |
| --- | --- |
| Tenho 20 minutos | `00` → `01` → `09` |
| Quero entender de verdade | `01` até `10`, na ordem |
| Vou avaliar um ETF agora | `09` (checklist), consultando `06` e `08` |

### Como ler os arquivos

São arquivos Markdown (`.md`). Você pode ler direto no GitHub, em qualquer editor de texto,
ou gerar PDF com Pandoc:

```bash
pandoc estudo/*.md -o fundamentos-etfs.pdf --toc --pdf-engine=xelatex -V geometry:margin=2.5cm
```

### Checklist na prática

O arquivo [`estudo/09-checklist-de-avaliacao-de-etf.md`](estudo/09-checklist-de-avaliacao-de-etf.md)
é o operacional. O fluxo é:

```
1. O que o ETF possui        (Bloco A)
2. Fundamento e preço        (Bloco B)
3. Projeção de retorno       (Bloco C, usando o arquivo 06)
4. Atrito até o meu bolso    (Bloco D, usando o arquivo 08)
5. Riscos e guard rails      (Bloco E)
```

---

## Parte 2 — Piloto SCHY (automação)

### Pré-requisitos

1. Crie o arquivo `.env` na raiz do projeto com:

```bash
ROIC_API_KEY=sua_chave_aqui
```

2. Use Python 3.12 ou superior.

### Pipeline P1 completo (recomendado)

Com `ROIC_API_KEY` no `.env`, configure também a taxa do seu plano:

```bash
ROIC_API_KEY=sua_chave_aqui
ROIC_REQUESTS_PER_MINUTE=300
```

Para testar se a API aceita essa velocidade antes de rodar o lote:

```bash
python3 scripts/test_roic_rate_limit.py --requests 60
```

```bash
python3 scripts/run_p1_pipeline.py --priority P1 --time-limit-seconds 7200
```

Isso executa, em sequência:

1. `sync_etf_registry.py` — cadastra ETFs do universo
2. `update_holdings.py` — baixa composições SEC que ainda faltam
3. `reprocess_compositions.py` — corrige ISIN/ticker nos snapshots já salvos
4. `resolve_asset_identities.py` — mapeia cada ativo na ROIC (com validação)
5. `fetch_p1_assets.py` — busca fundamentos **somente** de ativos verificados

Para rodar etapas separadas:

```bash
python3 scripts/sync_etf_registry.py
python3 scripts/update_holdings.py --priority P1
python3 scripts/reprocess_compositions.py --priority P1
python3 scripts/resolve_asset_identities.py --priority P1 --reset --time-limit-seconds 7200
python3 scripts/fetch_p1_assets.py --priority P1 --time-limit-seconds 7200
```

Para um ETF específico na coleta de composição:

```bash
python3 scripts/update_holdings.py --etf SCHY
```

### Levantamento ROIC dos ativos (P1)

O passo de fundamentos só processa ativos com identidade aprovada (`verified_isin`,
`verified_cusip`, `verified_symbol` ou `manual_approved`). Progresso fica no banco
(`asset_identities`, `asset_fundamental_fetches`) e em
`data/exports/fundamentals/p1/ativos_parciais.jsonl`.


Os dados ficam no banco `data/database/etf_screener.sqlite` e em
`data/exports/compositions/`. Detalhes em [`PLANO_DADOS.md`](PLANO_DADOS.md).

Hoje a composição ativa ainda vem da SEC. Vanguard e alguns iShares ficaram de fora.
O plano para passar a usar CSV/API das gestoras (e expandir o universo) está em
[`PLANO_EXTRACAO_COMPOSICOES.md`](PLANO_EXTRACAO_COMPOSICOES.md).

### 1. Construir o mapeamento de ações

Este passo resolve os nomes das empresas do ETF para os identificadores da ROIC.ai.

```bash
python3 scripts/build_schy_mapping.py
```

Para testar com poucas ações:

```bash
python3 scripts/build_schy_mapping.py --limit 10
```

O mapeamento fica salvo em `data/mappings/schy_symbols.json`.

### 2. Executar a extração e consolidação

```bash
python3 scripts/run_schy_pilot.py
```

Por padrão, o piloto processa as maiores posições até atingir **90% de cobertura limpa**
(dados validados). Para processar tudo:

```bash
python3 scripts/run_schy_pilot.py --full
```

Para testar com poucas ações:

```bash
python3 scripts/run_schy_pilot.py --limit 10
```

### 3. Conferir os resultados

Os arquivos são gerados em `data/output/schy/`:

- `composicao_etf.csv`
- `ativos.csv`
- `etf_consolidado.csv`
- `validacoes.csv`
- `excecoes.csv`
- `ajustes.csv`
- `run_summary.json`

### Observações do piloto

- O plano gratuito da ROIC.ai permite cerca de 5 requisições por minuto.
- O processo usa cache em `data/cache/` para evitar chamadas repetidas.
- A composição do ETF vem do arquivo SEC N-PORT salvo em `data/raw/`.
- Apenas posições em ações entram nos cálculos; os pesos das ações são normalizados para 100%.

---

## Parte 3 — Painel web (prova de conceito)

Interface para acompanhar ETFs, ativos e métricas consolidadas. Pode rodar **localmente** ou **na Vercel** (sem instalar nada no PC).

---

### Opção A — Publicar na Vercel (recomendado)

O painel roda inteiro na Vercel: site + API + banco de dados (SQLite embutido). Você só precisa de uma conta gratuita.

#### Passo a passo

1. Acesse [vercel.com](https://vercel.com) e faça login com sua conta GitHub.
2. Clique em **Add New → Project**.
3. Selecione o repositório **ETFs_Screener**.
4. Em **Root Directory**, clique em *Edit* e escolha a pasta **`frontend`**.
5. Deixe as demais opções como estão (Framework: Next.js, Build: `npm run build`).
6. Clique em **Deploy**.

Em 1–2 minutos você recebe um link tipo `https://etf-screener-xxxx.vercel.app`.

#### Atualizar os dados depois

Quando novos ETFs forem processados localmente:

```bash
python3 scripts/seed_schy_pilot.py          # ou pipeline completo no futuro
python3 scripts/calculate_etf_metrics.py --etf SCHY
cp data/database/etf_screener.sqlite frontend/data/
git add frontend/data/etf_screener.sqlite
git commit -m "Update dashboard database"
git push
```

A Vercel republica automaticamente a cada push no GitHub.

---

### Opção B — Rodar no seu computador

#### Pré-requisitos

1. Python 3.12+ (só se for regenerar o banco)
2. Node.js 18+

#### 1. Carregar dados do piloto SCHY (se ainda não tiver o banco)

```bash
python3 scripts/seed_schy_pilot.py
python3 scripts/calculate_etf_metrics.py --etf SCHY --auto-validate-schy
```

#### 2. Subir o painel

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:3000`.

> A API Python (`scripts/run_api.py`) não é mais necessária para o painel — tudo roda dentro do Next.js.

### O que você vê no painel

| Tela | Caminho | Conteúdo |
| --- | --- | --- |
| Resumo dos ETFs | `/` | Lista com filtro, ordenação e clique para detalhe |
| Detalhe do ETF | `/etf/SCHY` | Métricas consolidadas e top 10 ativos |
| Todos os ativos | `/ativos` | Empresas em ordem alfabética com métricas |

ETFs sem métricas calculadas aparecem na lista com "—" nos números.

### Scripts úteis

| Script | Função |
| --- | --- |
| `scripts/seed_schy_pilot.py` | Importa piloto SCHY (CSV → banco) |
| `scripts/calculate_etf_metrics.py` | Calcula e grava agregados por ETF |
| `frontend/scripts/prepare-db.mjs` | Copia o banco para o deploy (roda no build) |
| `scripts/run_api.py` | API Python local (opcional; Vercel usa a API do Next.js) |

---

## Sobre os números citados

Os dados de mercado no material de estudo são de **julho de 2026** e estão listados no final
de [`estudo/11-glossario-e-referencias.md`](estudo/11-glossario-e-referencias.md).

**Números de mercado envelhecem; fórmulas não.** Antes de usar o material para uma decisão,
atualize CAPE, earnings yield, prêmio de risco e projeções institucionais.

## O que este material não é

- **Não é recomendação de investimento.** É estudo e ferramenta de análise.
- **Não prevê o próximo ano.** Nada aqui tem poder preditivo abaixo de 10 anos.
- **Não trata de tributação individual.** Confirme com um contador.

## Manutenção

- Mudanças relevantes ficam registradas em [`CHANGELOG.md`](CHANGELOG.md).
- Se algum conteúdo mudar de forma que afete como você usa o material, este arquivo é
  atualizado junto.
