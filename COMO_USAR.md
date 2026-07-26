# Como usar

## Pré-requisitos

1. Crie o arquivo `.env` na raiz do projeto com:

```bash
ROIC_API_KEY=sua_chave_aqui
```

2. Use Python 3.12 ou superior.

## Piloto SCHY

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

## Observações

- O plano gratuito da ROIC.ai permite cerca de 5 requisições por minuto.
- O processo usa cache em `data/cache/` para evitar chamadas repetidas.
- A composição do ETF vem do arquivo SEC N-PORT salvo em `data/raw/`.
- Apenas posições em ações entram nos cálculos; os pesos das ações são normalizados para 100%.
