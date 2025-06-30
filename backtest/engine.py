# backtest/engine.py

import pandas as pd
from data.data_provider import get_data
from core.config import DETECTORS_BY_LEVEL

def run_backtest(
    source: str,
    symbol: str,
    timeframe: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
    levels: list[str],
    progress_callback=None
) -> dict:
    df = get_data(source, symbol, timeframe, start, end)

    # monta lista de detectores a executar, respeitando a ordem: Básico → Intermediário → Avançado
    detectors = []
    for lvl in levels:
        detectors.extend(DETECTORS_BY_LEVEL.get(lvl, []))

    total = len(detectors)
    results = {}
    for i, detector in enumerate(detectors, start=1):
        results[detector.__name__] = detector(df)
        if progress_callback:
            progress_callback(int(i / total * 100))
    return results

