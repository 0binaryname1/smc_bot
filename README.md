# smc\_bot

**Biblioteca Python para detecção de Smart Money Concepts (SMC) em dados de mercado e backtesting.**

---

## Sumário

* [Visão Geral](#visão-geral)
* [Estrutura do Projeto](#estrutura-do-projeto)
* [Instalação](#instalação)
* [Uso](#uso)
* [Configuração](#configuração)
* [Testes](#testes)
* [Próximos Passos](#próximos-passos)

---

## Visão Geral

O **smc\_bot** é uma ferramenta para automatizar a análise de padrões de Smart Money Concepts (SMC) — como Break of Structure (BOS), Change of Character (CHOCH), Fair Value Gaps (FVG) e muito mais — e executar simulações (backtesting) de estratégias baseadas nesses padrões. Ideal para traders e pesquisadores que desejam validar hipóteses de SMC de forma programática.

---

## Estrutura do Projeto

```
smc_bot/
├── backtest/               # Engine de backtest e simulação
│   └── engine.py           # Função run_backtests
├── core/                   # Módulos centrais de detecção de padrões
│   ├── patterns.py         # Funções detect_bos, detect_choch, detect_fvg, etc.
│   └── config.py           # Parâmetros globais para detectores
├── data/                   # Acesso e preparação de dados históricos
│   ├── data_provider.py    # Cache local e interface genérica de dados
│   ├── fetchers/           # Adaptadores para Yahoo Finance e AlphaVantage
│   │   ├── yf_fetcher.py
│   │   └── av_fetcher.py
│   └── data_assets/        # Scripts para converter CSVs brutos em Parquets
│       └── prepare_data.py
├── gui/                    # (Protótipo) Interface gráfica futura
├── tests/                  # Testes automatizados com pytest
│   ├── test_patterns_basic.py
│   ├── test_patterns_real.py
│   └── test_patterns_intermediate.py
├── main.py                 # Script de entrada principal
├── config.py               # Configurações e mapeamento de ativos
├── README.md               # Documentação principal
├── requirements.txt        # Dependências do projeto
└── pyproject.toml          # Metadados e empacotamento
```

---

## Instalação

Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.\.venv\Scripts\activate     # Windows PowerShell
```

Instale dependências:

```bash
pip install -r requirements.txt
```

---

## Uso

1. Obtenha dados brutos (CSV M1) e gere Parquets para acelerar leituras:

   ```bash
   python data/data_assets/prepare_data.py
   ```
2. Execute o backtest para múltiplos ativos:

   ```bash
   python main.py --timeframe 15m --start 2023-01-01
   ```
3. Importe e use as funções no seu código:

   ```python
   from core.patterns import detect_bos, detect_fvg
   df = ...  # DataFrame de candles
   print(detect_bos(df), detect_fvg(df))
   ```

---

## Configuração

Edite `config.py` para ajustar:

* `ASSETS`: dicionário de símbolos e nomes amigáveis.
* `TIMEFRAME`: valor padrão para timeframe (e.g. "15m").
* `START_DATE`: data inicial para testes.

---

## Testes

Execute todos os testes com pytest:

```bash
pytest -q
```

Ou testes específicos:

```bash
pytest tests/test_patterns_intermediate.py -q
```

---

## Próximos Passos

* **Nível Avançado (20% concluído)**: atualmente 3 de 15 detectores/funcionalidades implementados (MSS, Breaker Blocks, Confluence Zones, Mitigation Blocks, FVG múltiplos, Liquidity Voids, Stop Hunts etc.) estão planejados.
* **Nível Intermediário (100% concluído)**: detectores de Inducement, Premium/Discount Zone e Kill Zones implementados e testados.
* **Nível Básico (100% concluído)**: detectores de BOS, CHOCH, FVG, Order Blocks, Liquidity Zones, Liquidity Sweep estão implementados, documentados e com cobertura de testes automáticos.
* **Testes**: 60/60 testes passaram, cobrindo cenários sintéticos e reais.
* **Documentação**: README.md atualizado com descrições de todos os arquivos e status do projeto.
* **Pipeline**: preparar CI/CD e Docker para executar backtest de forma isolada.

---

*Com base na execução de 8 meses de desenvolvimento, estimamos \~40% do roadmap global concluído.*

