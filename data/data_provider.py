import pandas as pd
from pathlib import Path

def get_data_local(symbol: str, timeframe: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    assets_dir = Path(__file__).parent / "data_assets"
    # Espera arquivos nomeados como SYMBOL_TIMEFRAME.parquet, ex. "BTCUSD_M1.parquet"
    path = assets_dir / f"{symbol}_{timeframe}.parquet"
    df = pd.read_parquet(path)
    # Supondo existência de coluna datetime
    return df[(df["datetime"] >= start) & (df["datetime"] <= end)].reset_index(drop=True)

def get_data(source: str, symbol: str, timeframe: str, start, end):
    if source == "parquet":
        return get_data_local(symbol, timeframe, start, end)
    elif source == "csv":
        return get_data_csv(symbol, timeframe, start, end)
    else:
        raise ValueError(f"Fonte desconhecida: {source}")
