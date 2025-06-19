import pickle
import tempfile
from pathlib import Path
import pandas as pd

from data.fetchers.yf_fetcher import fetch_yf
from data.fetchers.av_fetcher import fetch_av

# >>> (A) Defina o diret├│rio de cache no topo, antes de get_data
CACHE_DIR = Path(tempfile.gettempdir()) / "smc_bot_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_data(..., cache_dir: Path | None = None) -> pd.DataFrame:
    cache_dir = Path(cache_dir or CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    #  ΓööΓåÆ este mkdir garante que o dp.CACHE_DIR (apesar do monkeypatch) existe
    fname = f"{symbol.replace('/', '-')}-{timeframe}_{start}_{end}_{provider}.pkl"
    cache_path = cache_dir / fname

    # 1) tenta carregar do cache
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    # 2) baixa via API
    ...
    # 3) normaliza colunas
    df = df.rename(columns=str.lower)[["open","high","low","close"]]

    # 4) salva no cache
    with open(cache_path, "wb") as f:
        pickle.dump(df, f)

    return df.

    # 2) SE N├âO HOUVER CACHE, BAIXAR VIA API
    if provider == "yf":
        df = fetch_yf(symbol, timeframe, start, end)
    elif provider == "av":
        if not api_key:
            raise ValueError("Para AlphaVantage, forne├ºa api_key")
        df = fetch_av(symbol, timeframe, start, end, api_key=api_key)
    else:
        raise ValueError(f"Provider inv├ílido: {provider!r}")

    # 3) NORMALIZAR COLUNAS (se necess├írio no seu projeto)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close"]]

    # 4) **SALVAR NO CACHE**: ├⌐ aqui que gravamos em disco para a pr├│xima vez
    with open(cache_path, "wb") as f:
        pickle.dump(df, f)

    return df
