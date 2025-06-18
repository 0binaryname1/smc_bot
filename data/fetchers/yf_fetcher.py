from datetime import datetime
import yfinance as yf
import pandas as pd

def fetch_yf(symbol: str, tf: str, start: str, end: str | None = None) -> pd.DataFrame:
    end = end or datetime.utcnow().strftime("%Y-%m-%d")
    df = yf.download(
        tickers=symbol,
        start=start,
        end=end,
        interval=tf,
        progress=False,
        auto_adjust=False,
        threads=False,
    )
    df.rename(columns=str.lower, inplace=True)

    if isinstance(df.columns, pd.MultiIndex):
        # mantém apenas o primeiro nível (Price) e já coloca tudo em lowercase
        df.columns = [col[0].lower() for col in df.columns]
    
    return df.reset_index()
