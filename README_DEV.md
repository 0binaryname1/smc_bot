📘 Projeto: smc_bot

Propósito: Automatizar operações financeiras com base em análise técnica do tipo Smart Money Concepts (SMC), organizando os módulos em diferentes níveis de complexidade para operação autônoma.


---

📁 Estrutura do Projeto

smc_bot/
├── backtest/               # Engine de backtest e simulação
├── core/                   # Algoritmos principais de detecção de padrões SMC
├── data/                   # Acesso a dados, cache e provedores
├── gui/                    # Interface do usuário
├── tests/                  # Testes automatizados com pytest
├── trade/                  # Módulo de execução de trades (placeholder)
├── main.py                 # Script de entrada principal
├── config.py               # Parâmetros globais
├── requirements.txt        # Dependências para produção
├── pyproject.toml          # Metadados do projeto (build via setuptools)
├── README_DEV.md           # Este arquivo


---

## 1. Visão Geral do Projeto

- **Nome:** smc_bot
- **Descrição:** Biblioteca Python para detecção de padrões Smart Money Concepts (SMC), obtenção de dados financeiros (Yahoo Finance, AlphaVantage), cache local, e testes automatizados.
- **Principais Módulos:**
  - `core/patterns.py`: funções para detecção de BOS, CHOCH, FVG, Order Blocks, Liquidity Zones, Liquidity Sweeps, e níveis avançados.
  - `data/data_provider.py`: lógica de download e cache de séries históricas.
  - `data/fetchers/yf_fetcher.py`: adaptador para Yahoo Finance (yfinance).
  - `tests/`: suíte de testes unitários cobrindo casos básicos de cada função.

## 2. Ambiente de Desenvolvimento

1. **Clonar repositório**:
   ```bash
   git clone git@github.com:0binaryname1/smc_bot.git
   cd smc_bot
   ```
2. **Criar e ativar ambiente**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .\.venv\Scripts\activate   # Windows PowerShell
   ```
3. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Executar testes**:
   ```bash
   pytest tests
   ```

## 3. Estado Atual

- **Funcionalidades básicas** (nível _basic_) implementadas e com testes verdes:
  - Break of Structure (BOS)
  - Change of Character (CHOCH)
  - Fair Value Gaps (FVG)
  - Order Blocks
  - Liquidity Zones
  - Liquidity Sweeps
- **Data Provider** com cache local via pickle funcionando.
- **Adapter** para Yahoo Finance (`fetch_yf`) validado.

## 4. Próximos Passos & Tarefas Pendentes

1. **Cobertura de testes**:
   - Criar testes unitários para padrões _intermediários_ e _avançados_ (Kill Zones, Inducement, Breaker Blocks, Confluence).
   - Adicionar cenários extremos e casos negativos.
2. **Implementação de nível intermediário/avançado**:
   - `detect_killzones`, `detect_inducement`, `detect_breaker_blocks`, `detect_confluence_zones` em `core/patterns.py`.
3. **Backtesting Intraday**:
   - Integrar fonte de dados intraday gratuita da B3 (via API pública ou CSV historicamente disponível).
   - Escrever módulo de _backtest_ que consome `data_provider` e `core/patterns` para validar sinais em dados reais.
4. **Interface Gráfica**:
   - Prototipar GUI com Streamlit ou React/Tailwind (conforme planejado).
5. **Documentação & Deploy**:
   - Atualizar documentação de uso na raiz (`README.md`).
   - Configurar CI (GitHub Actions) para rodar testes e lint.

## 5. Referências & Recursos

- PDF anexados no repositório:
  - SMART-MONEY-TRADING-GUIDE.pdf
  - SMC Bible (DexterrFX).pdf
  - Smart-Money-Concept-trading-strategy-PDF.pdf
- Artigos ICT, Tom Williams, Steve Mauro (BTMM).




---

📦 Dependências

Estão listadas em requirements.txt, incluindo:

pandas, numpy, pytest

yfinance, alpha_vantage, streamlit


Para instalar:

pip install -r requirements.txt


---

🤝 Contribuição

O projeto aceita modificações tanto pelo desktop (Windows + Git) quanto por celular (Termux + SSH + Git).

Commits devem seguir padrões semânticos (feat:, fix:, docs:).



---

> Documento gerado automaticamente para facilitar a transição entre o agente Codex e desenvolvedor humano.



🧠 Próxima meta: nivelar e validar todos os testes do nível básico antes de subir para intermediário.


