import pandas as pd
from data.fetchers.yf_fetcher import fetch_yf

def test_fetch_btc_daily():
    df = fetch_yf("BTC-USD", "1d", "2024-01-01", "2024-01-03")
    # Deve retornar DataFrame não vazio e com colunas mínimas em lowercase
    assert not df.empty
    cols = {c.lower() for c in df.columns}
    assert {"open", "high", "low", "close"}.issubset(cols)
