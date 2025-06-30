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
* [Status de Conclusão](#status-de-conclusão)
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
│   ├── patterns.py         # Funções detect_bos, detect_choch, detect_fvg etc.
│   └── config.py           # Parâmetros globais para detectores
├── data/                   # Acesso e preparação de dados históricos
│   ├── data_provider.py    # Cache local e interface de dados
│   ├── fetchers/           # Adaptadores para Yahoo/AlphaVantage
│   └── data_assets/        # Scripts de conversão CSV → Parquet
├── gui/                    # (Protótipo) Interface gráfica
├── tests/                  # Testes automatizados com pytest
│   ├── test_patterns_basic.py
│   ├── test_patterns_real.py
│   ├── test_patterns_intermediate.py
│   └── test_patterns_advanced.py
├── main.py                 # Script de entrada principal
├── config.py               # Mapeamento de ativos e configurações padrão
├── README.md               # Documentação do projeto
├── requirements.txt        # Dependências Python
└── pyproject.toml          # Metadados e empacotamento
```

---

## Instalação

Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.\.venv\Scripts\activate     # Windows PowerShell
```

Instale dependências:

```bash
pip install -r requirements.txt
```

---

## Uso

1. **Preparar dados** (CSV M1 → Parquet):

   ```bash
   python data/data_assets/prepare_data.py
   ```
2. **Executar backtest** para ativos definidos:

   ```bash
   python main.py --timeframe 15m --start 2023-01-01
   ```
3. **Importar detectores** em scripts:

   ```python
   from core.patterns import detect_bos, detect_fvg
   df = ...  # Candles
   print(detect_bos(df), detect_fvg(df))
   ```

---

## Configuração

Ajuste `config.py`:

* `ASSETS`: dicionário nome→símbolo.
* `TIMEFRAME`, `START_DATE`: parâmetros padrão.

---

## Testes

Execute todos os testes:

```bash
pytest -q
```

Testes por nível:

```bash
pytest tests/test_patterns_basic.py -q
pytest tests/test_patterns_intermediate.py -q
pytest tests/test_patterns_advanced.py -q
```

---

## Status de Conclusão

* **Nível Básico**: 100% concluído (6/6 padrões).
* **Nível Intermediário**: 100% concluído (3/3 padrões).
* **Nível Avançado**: 20% concluído (3/15 detectores).
* **Cobertura de Testes**: 64 testes automatizados passando.
* **Documentação**: README.md atualizado com descrição completa de arquivos e status.
* **Conclusão Global**: \~40% do roadmap global concluído.

---

## Próximos Passos

* **Implementar detectores avançados restantes**: MSS refinado, Mitigation Blocks, Liquidity Voids, Stop Hunts, FVG múltiplos, etc.
* **Integração no Backtest**: incluir sinais avançados e validar resultados end-to-end.
* **CI/CD**: configurar GitHub Actions para testes e lint.
* **Docker**: criar contêiner para backtesting padronizado.
* **Interface Gráfica**: evoluir protótipo em `gui/`.

> *Desenvolvido com base em conceitos de Smart Money Concepts e práticas de backtesting em Python.*

```
```

