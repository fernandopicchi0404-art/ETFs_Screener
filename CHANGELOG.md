# Changelog

## Em desenvolvimento

- Corrige mapeamentos manuais ambíguos do SCHY (BOC Hong Kong, Imperial Brands, Kone, Tung Ho, Saudi Telecom).
- Adiciona retries para timeout de rede na API ROIC e continua o mapeamento mesmo após erro por ativo.
- Corrige extração de patrimônio anterior quando a ROIC retorna apenas um exercício.
- Adiciona mapeamentos manuais para Schroders, Kuehne+Nagel, TMBThanachart e Gjensidige.
- Documenta a análise exclusiva das posições em ações e a normalização de seus pesos para 100%.
- Separa dividend yield, buyback yield e shareholder yield.
- Define o tratamento de lucro, minoritários, ações diluídas, patrimônio médio e ROE.
- Especifica validações, ajustes externos, exceções, CSVs e abas do relatório Excel.
- Implementa pipeline de composição SEC, mapeamento ROIC, extração de fundamentos e consolidação do SCHY.
