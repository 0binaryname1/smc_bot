# smc\_bot

**Biblioteca Python para operações financeiras autônomas baseadas em Smart Money Concepts (SMC)**

---

## 🧩 Visão Geral

smc\_bot é uma ferramenta modular que detecta padrões de Smart Money Concepts (SMC) em dados OHLC (Open, High, Low, Close) históricos, permite backtests locais via interface Tkinter e inclui suíte de testes automatizados.

**Objetivos principais:**

* Oferecer detectores de padrões SMC que funcionem apenas com OHLC, sem dependência de APIs externas.
* Backtest local on‑demand via GUI Tkinter, com seleção de arquivo CSV/Parquet e níveis de análise configuráveis.
* Logs em tempo real e relatório de resultados de performance dos detectores.
* Estrutura de código e testes que facilite continuidade em novos chats ou por outros desenvolvedores.

---

## 📂 Estrutura do Projeto

```
smc_bot/
├── core/                  # Detectores de padrões SMC (OHLC-only)
│   ├── patterns.py        # Funções básicas, intermediárias e avançadas sem volume
│   └── config.py          # Parâmetros globais e lista DETECTORS_BY_LEVEL
├── backtest/
│   └── engine.py          # run_backtest_df: executa detectores sobre DataFrame
├── app_tk.py              # GUI Tkinter: abas Análise, Log, Resultados
├── tests/                 # Pytest: cobertura unitária de todos os detectores
│   ├── test_patterns_basic.py
│   ├── test_patterns_intermediate.py
│   └── test_patterns_advanced.py
├── config.py              # Configurações de ativos/timeframes padrões
├── .gitignore             # Ignora data assets, logs, ambientes
└── README.md              # Este arquivo
```

**Não mantidos (versões offline/internas):** módulos de fetchers (Yahoo, AlphaVantage), GUI Streamlit, data\_assets versionadas. Esses padrões são carregados pelo usuário via seleção de arquivo local.

---

## ⚙️ Instalação e Preparação

1. Clone o repositório:

   ```bash
   git clone https://github.com/0binaryname1/smc_bot.git
   cd smc_bot
   ```
2. Crie e ative ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .\.venv\Scripts\activate  # Windows PowerShell
   ```
3. Instale dependências:

   ```bash
   pip install -r requirements.txt
   ```

> **Observação:** `requirements.txt` inclui apenas pacotes necessários para OHLC-only (pandas, numpy, pytest, tkinter está no stdlib).

---

## 🚀 Uso da Interface Tkinter

Para iniciar a GUI:

```bash
python app_tk.py
```

### Abas Principais

1. **Análise**

   * Botão para importar CSV ou Parquet de dados OHLC.
   * Checkboxes para escolher níveis de detectores: Básico, Intermediário, Avançado.
   * Calendário dinâmico (em desenvolvimento) para intervalo de datas.
   * Botão **Rodar Backtest** inicia processamento em thread separada.

2. **Log de Análise**

   * Barra de progresso verde indicando quantos detectores foram executados.
   * Área de texto que exibe passo a passo: leitura de arquivo, execução de cada detector, capturas de erro.

3. **Resultados**

   * Exibe métricas por detector: número de sinais, taxa de acerto (Win Rate), profit factor, expectancy.
   * Futuramente: gráficos de capital, tabela de trades.

---

## 🔧 Execução de Testes

Para validar a suíte de detectores:

```bash
pytest -q
```

Todos os testes unitários em `tests/` devem passar (60+ testes cobrindo todos os padrões).

---

## 📈 Próximos Passos

* **Calendar Picker:** concluir seleção de intervalo de datas na GUI.
* **Resultados Avançados:** implementar cálculo de métricas financeiras (Profit Factor, Drawdown, Sharpe).
* **Módulo de Volume (opcional):** criar `core/patterns_volume.py` para dependências de volume/OFI.
* **Relatório Gráfico:** adicionar geração de gráficos ao GUI ou exportação CSV/PPT.
* **Persistência de Backtests:** salvar logs e resultados em arquivos para comparativos históricos.

**OBS:** Este README serve como passagem de serviço; ao mudar de chat ou máquina, siga estes passos para retomar o projeto imediatamente.

