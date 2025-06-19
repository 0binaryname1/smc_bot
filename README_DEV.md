# SMC\_BOT - README DEV

## 🔢 Visão Geral

Este projeto implementa um sistema automatizado de detecção de padrões baseado no Smart Money Concepts (SMC) e ICT (Inner Circle Trader), com foco em aplicações para Ações, Forex, Criptomoedas e Futuros. Inclui um motor de backtest, detecção de estrutura de mercado e uma GUI via `streamlit`.

> Ambiente validado no Windows via PowerShell e Android (Termux), com sincronização via GitHub.

---

## 🔹 Módulos Implementados

### Nível Básico - `core/patterns.py`

* `detect_bos(df)` - Break of Structure
* `detect_order_blocks(df)`
* `detect_fvg(df)` - Fair Value Gap
* `detect_liquidity_zones(df)` - zonas de liquidez baseadas em repetções
* `detect_liquidity_sweep(df)` - rompimento agressivo das zonas acima

### Nível Intermediário

* `detect_choch(df)` - Change of Character
* `detect_inducement(df)`
* `detect_premium_discount(df)`
* `detect_killzones(df, ts_col)`

### Execução e Validação

* `is_continuation_valid(df)`
* `is_reversal_valid(df)`

---

## 🔮 Estrutura de Testes - `tests/test_patterns_basic.py`

Todos os testes estão em conformidade com o PyTest e testam:

* Casos positivos e negativos para `bos`, `order_blocks`, `fvg`
* Precisão de zonas de liquidez com tolerância
* Detecção de sweeps com critério de corpo do candle (>70%)

> A maioria dos testes **passou**, exceto por:

* `test_detect_fvg` - esperado um FVG inexistente (corrigir dados do teste)
* `test_detect_order_blocks` - ordem esperada difere da real (ajustar assert)
* `test_detect_liquidity_zones` - retornar apenas zonas com métrica robusta (precisa ajustar o critério)
* `test_detect_liquidity_sweep` - falha por falta de sweep (corrigir dados do teste)

---

## 🔧 Ajustes Necessários - `core/data_provider.py`

### Problema

Os testes de cache e carregamento de `get_data()` com `fetch_yf` e `fetch_av` falham nos asserts por `df1 is df2`.

### Solução

Substituir:

```python
assert out is df_dummy
```

por:

```python
pd.testing.assert_frame_equal(out, df_dummy)
```

E replicar nas demais chamadas.

---

## 🚀 Orientação ao Codex

Este repositório é um sistema de detecção de padrões de preço baseados no Smart Money Concepts. As etapas de detecção devem ser evoluídas seguindo a hierarquia:

* **Nível Básico:** estrutura de mercado (BOS, CHoCH), gaps, blocks, liquidez.
* **Nível Intermediário:** inducements, zonas premium/discount, armadilhas.
* **Nível Avançado:** breaker blocks, mitigação, SMT, confluências.

🔗 O Codex pode ser usado para:

* Refatorar os testes PyTest
* Validar estratégias completas com pandas
* Evoluir os padrões intermediários
* Criar scripts de exportação/análise

> Utilize os arquivos `patterns.py`, `test_patterns_basic.py`, `data_provider.py` e `gui/smc_gui.py` como base principal de edição.

---

## 📊 Roadmap

| Etapa                     | Status      | Responsável  |
| ------------------------- | ----------- | ------------ |
| Detecção de BOS e CHoCH   | ✅ Feito     | Chat + User  |
| Order Blocks + FVG        | ✅ Feito     | Chat + User  |
| Liquidez (zona + sweep)   | ✅ Testado   | User         |
| Ajustes nos asserts       | ⚠️ Pendente | User         |
| Padronização `config.py`  | ✅ Feito     | Chat         |
| Refatorar GUI (streamlit) | ⚠️ Parcial  | Chat + User  |
| Modularização Avançada    | ⏳ Em breve  | Codex + Chat |

---

Para execução local:

```bash
git pull
python -m pytest tests -v
streamlit run gui/smc_gui.py
```

