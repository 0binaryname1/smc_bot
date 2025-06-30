import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from backtest.engine import run_backtest
from core.config import ASSETS, TIMEFRAMES, START_DATE

st.set_page_config(page_title="SMC Bot Backtest")
st.title("SMC Bot Backtest")

# Novo selectbox de fonte:
source = st.selectbox("Fonte de Dados", ["parquet", "csv"])

symbol = st.selectbox("Ativo", ASSETS)
timeframe = st.selectbox("Timeframe", TIMEFRAMES, index=TIMEFRAMES.index("M1"))
start = st.date_input("Data Início", value=START_DATE.date())
end = st.date_input("Data Fim", value=pd.Timestamp.now().date())

levels = st.multiselect(
    "Níveis de Detectores",
    ["Básico", "Intermediário", "Avançado"],
    default=["Básico"]
)

if start > end:
    st.error("Data de início deve ser anterior à data de fim")
elif st.button("Backtest"):
    progress_bar = st.progress(0)
    try:
        def _update(p): progress_bar.progress(p)
        results = run_backtest(
            source,
            symbol,
            timeframe,
            pd.Timestamp(start),
            pd.Timestamp(end),
            levels,
            progress_callback=_update
        )
        st.success("Backtest concluído")
        st.json(results)
    except FileNotFoundError:
        st.error("Dados não encontrados para o ativo/timeframe selecionado")
    except Exception as e:
        st.error(f"Erro durante backtest: {e}")

