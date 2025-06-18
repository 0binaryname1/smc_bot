import os
import pandas as pd
from alpha_vantage.timeseries import TimeSeries

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
if not API_KEY:
    raise RuntimeError("Defina a variável ALPHAVANTAGE_API_KEY com sua chave Alpha Vantage")

def fetch_av(symbol: str, tf: str, start: str) -> pd.DataFrame:
    """
    tf: '1min','5min','15min','30min','60min','daily'
    start: 'YYYY-MM-DD'
    """
    ts = TimeSeries(key=API_KEY, output_format="pandas")
    if tf == "daily":
        data, _ = ts.get_daily(symbol, outputsize="full")
    else:
        data, _ = ts.get_intraday(symbol, interval=tf, outputsize="full")
    data = data.loc[start:]
    # padroniza colunas e renomeia para lowercase
    data.columns = [c.lower() for c in data.columns]
    data = data.rename_axis("date").reset_index()
    return data
