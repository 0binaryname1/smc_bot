# smc\_bot

**Biblioteca Python para detecção de padrões Smart Money Concepts (SMC).**

## Estrutura do Repositório

```
smc_bot/
├── backtest/                 # Motor de backtest e simulação (em planejamento)
├── core/                     # Implementação dos detectores de padrões SMC
│   └── patterns.py           # Funções básicas e intermediárias de SMC
├── data/
│   └── data_assets/          # Scripts e arquivos de dados brutos e processados
│       ├── prepare_data.py   # Converte CSVs M1 em Parquet em chunks
│       ├── BTC/parquets/     # Saída de arquivos parquet do BTCUSD M1
│       └── (outros ativos)
├── gui/                      # Protótipo de interface (pendente)
├── tests/                    # Testes automatizados com pytest
│   ├── test_patterns_basic.py   # Casos unitários de padrões básicos
│   └── test_patterns_real.py    # Validação em dados reais (chunks de 12h)
├── main.py                   # Ponto de entrada (pendente)
├── config.py                 # Parâmetros globais e variáveis de ambiente
├── requirements.txt          # Dependências do projeto (+ pyarrow para Parquet)
└── README_DEV.md             # Documento de desenvolvimento (este arquivo)
```

## Progresso de Hoje (Produção)

* Pipeline de dados: CSVs M1 de BTCUSD convertidos em Parquet via `prepare_data.py`.
* Implementação e testes: funções básicas SMC (`detect_bos`, `detect_choch`, `detect_fvg`, `detect_order_blocks`, `detect_liquidity_zones`, `detect_liquidity_sweep`) totalmente validadas em cenários sintéticos e reais.
* Infraestrutura de testes: `pytest` configurado, fixtures de leitura de Parquet por glob, chunks de 12h com semente fixa para determinismo.

## Próximos Passos

1. Desenvolver e testar detectores de nível intermediário (inducement, premium/discount, killzones, breakers, confluence).
2. Integrar módulo de execução de trades e backtesting intraday.
3. Prototipar interface gráfica (Streamlit ou React/Tailwind).
4. Escrever CI/CD (GitHub Actions) para pipeline de testes e lint.

## Percentual de Conclusão

* **Nível Básico (detectores + testes): 100% concluído**
* **Pipeline de dados (CSV→Parquet): 100% concluído**
* **Nível Intermediário: 0%**
* **Backtest & interface gráfica: 0%**

> **Total aproximado de conclusão global: 25%**

---

### Como usar hoje

1. Coloque os CSVs originais em `data/data_assets/`.
2. Execute:

   ```bash
   python data/data_assets/prepare_data.py
   pytest -q
   ```
3. Verifique relatórios de cobertura em `tests/coverage/` (quando implementado).
