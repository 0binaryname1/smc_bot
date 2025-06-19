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

✅ Etapas concluídas

[x] Estrutura do projeto padronizada

[x] Detecção SMC Básico: BOS, CHoCH, FVG, Order Blocks, Liquidez

[x] pytest implementado com mocks e validações

[x] Integração com Codex verificada

[x] Correção do bug assert is substituído por assert_frame_equal



---

⚠️ O que precisa ser feito

🧪 Ajustes de testes (nível básico)

test_detect_order_blocks()

Corrigir esperados com base no real comportamento (possível confusão entre vela e pullback)


test_detect_fvg()

Verificação de gaps realistas com candlesticks anteriores


test_detect_liquidity_zones()

Usar np.allclose para comparar floats

Usar tolerance e min_touches


test_detect_liquidity_sweep()

Ajustar os índices com base na lógica de body_ratio e confirmação



⚙️ Refatorar data_provider

Garantir que o mock de fetch_yf e fetch_av não seja comparado por identidade (is) e sim por equals()



---

💡 Orientação ao agente Codex

1. Executar os testes com pytest tests/ a cada commit.


2. Corrigir os testes que ainda falham usando pytest -v para detalhes.


3. Dar prioridade para deixar o nível básico 100% verde antes de seguir.


4. Em seguida, iniciar o nível intermediário (inducement, premium_discount, killzones).


5. Qualquer alteração em patterns.py deve manter compatibilidade com os testes.




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


