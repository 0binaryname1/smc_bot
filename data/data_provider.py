import os
import pickle
from pathlib import Path

import pandas as pd

from data.fetchers.yf_fetcher import fetch_yf
from data.fetchers.av_fetcher import fetch_av

CACHE_DIR = Path(__file__).parent.parent / "cache"

def get_data(
    symbol: str,
    timeframe: str,
    start: str,
    end: str,
    provider: str = "yf",
    api_key: str | None = None,
    cache_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Baixa dados históricos ou retorna do cache local.
    
    Parâmetros:
      - symbol: ex. "BTC-USD" ou "EURUSD=X"
      - timeframe: ex. "1d", "15m"
      - start, end: "YYYY-MM-DD"
      - provider: "yf" (YahooFinance) ou "av" (AlphaVantage)
      - api_key: obrigatório se provider="av"
      - cache_dir: pasta onde gravar .pkl; se None usa DEFAULT
    
    Retorna DataFrame com colunas ['open','high','low','close'].
    """
    cache_dir = Path(cache_dir or CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{symbol.replace('/', '-')}_{timeframe}_{start}_{end}_{provider}.pkl"
    cache_path = cache_dir / fname

    # 1) tenta carregar do cache
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            df = pickle.load(f)
        return df

    # 2) baixa via API
    if provider == "yf":
        df = fetch_yf(symbol, timeframe, start, end)
    elif provider == "av":
        if not api_key:
            raise ValueError("Para AlphaVantage, forneça api_key")
        df = fetch_av(symbol, timeframe, start, end, api_key=api_key)
    else:
        raise ValueError(f"Provider inválido: {provider!r}")

    # 3) normaliza colunas
    df = df.rename(columns=str.lower)[["open","high","low","close"]]

    # 4) salva no cache
    with open(cache_path, "wb") as f:
        pickle.dump(df, f)

    return df
