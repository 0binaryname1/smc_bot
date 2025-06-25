# core/patterns.py

"""
Smart Money Concepts (SMC) pattern detection functions.
This module provides basic SMC pattern detection such as Break of Structure (BOS),
Change of Character (CHOCH), Fair Value Gaps (FVG), Order Blocks, liquidity zones, and liquidity sweeps.
"""

import numpy as np
import pandas as pd

def detect_bos(df: pd.DataFrame) -> bool:
    if df is None or len(df) < 2:
        return False

    highs = df['high']
    lows  = df['low']
    closes= df['close']

    # Identifica últimos swings relevantes
    last_swing_high = highs.iloc[:-1].iloc[::-1].max()
    last_swing_low  = lows .iloc[:-1].iloc[::-1].min()

    # Candle de rompimento deve fechar além do swing
    if closes.iat[-1] > last_swing_high:
        return True
    if closes.iat[-1] < last_swing_low:
        return True
    return False

def detect_fvg(df: pd.DataFrame) -> list[tuple[float, float]]:
    gaps = []
    if df is None or len(df) < 2:
        return gaps

    highs = df['high']
    lows  = df['low']

    for i in range(1, len(df)):
        prev_h = highs.iat[i-1]
        prev_l = lows .iat[i-1]
        curr_h = highs.iat[i]
        curr_l = lows .iat[i]

        # gap de alta: mínima do atual acima da máxima anterior
        if curr_l > prev_h:
            gaps.append((prev_h, curr_l))

        # gap de baixa: máxima do atual abaixo da mínima anterior
        elif curr_h < prev_l:
            gaps.append((curr_h, prev_l))

    return gaps

def detect_order_blocks(df: pd.DataFrame, min_range: float = 0) -> list[dict]:
    """
    Retorna lista de dicts: {"index":i, "type":"bullish"/"bearish", "zone":(low,high)}.
    """
    obs = []
    curr_max = df['high'].iat[0]
    curr_min = df['low'] .iat[0]

    for i in range(1, len(df)):
        h, l, o, c = df['high'].iat[i], df['low'].iat[i], df['open'].iat[i], df['close'].iat[i]
        prev_h, prev_l, prev_o, prev_c = df['high'].iat[i-1], df['low'].iat[i-1], df['open'].iat[i-1], df['close'].iat[i-1]

        # bullish BOS confirmado por fechamento
        if c > curr_max and df['close'].iat[i] > curr_max:
            # candle anterior devia ser bearish e ter range suficiente
            if prev_c < prev_o and abs(prev_h - prev_l) >= min_range:
                obs.append({"index":i-1, "type":"bullish", "zone":(prev_l, prev_h)})
            curr_max = h

        # bearish BOS
        if c < curr_min and df['close'].iat[i] < curr_min:
            if prev_c > prev_o and abs(prev_h - prev_l) >= min_range:
                obs.append({"index":i-1, "type":"bearish", "zone":(prev_l, prev_h)})
            curr_min = l

    # remove duplicatas por índice
    uniq = {o["index"]:o for o in obs}
    return list(uniq.values())

def detect_liquidity_zones(df: pd.DataFrame, min_touches: int = 2, tol: float = 1e-5) -> dict[float,int]:
    """
    Retorna dict {price: count} para each level tocado >= min_touches.
    """
    counts = {}
    for price in list(df['high']) + list(df['low']):
        # junta highs e lows
        counts[price] = counts.get(price, 0) + 1

    # agrupar por proximidade tol e filtrar
    zones = {}
    for price, cnt in counts.items():
        # encontra key já existente próxima
        found = next((z for z in zones if abs(z - price) <= tol), None)
        if found:
            zones[found] += cnt
        else:
            zones[price] = cnt

    # só retorna as que tiveram toques suficientes
    return {z:c for z,c in zones.items() if c >= min_touches}

def detect_liquidity_sweep(df: pd.DataFrame, zones: list[float], body_ratio: float = 0.5, tol: float = 1e-5) -> list[dict]:
    """
    Para cada zona z, verifica se candle fura e fecha do outro lado com pavio.
    Retorna list de {"index":i, "level":z, "direction":"up"/"down"}.
    """
    sweeps = []

    highs = df['high']; lows = df['low']; closes = df['close']; opens = df['open']
    for i in range(1, len(df)):
        h, l, o, c = highs.iat[i], lows.iat[i], opens.iat[i], closes.iat[i]
        rng  = h - l
        body = abs(c - o)
        if rng == 0: continue
        if body / rng > body_ratio:
            continue  # exige sombra grande

        for z in zones:
            # sweep buy‐side: fura acima z e fecha abaixo
            if h > z + tol and c < z - tol:
                sweeps.append({"index":i, "level":z, "direction":"up"})
            # sweep sell‐side: fura abaixo z e fecha acima
            if l < z - tol and c > z + tol:
                sweeps.append({"index":i, "level":z, "direction":"down"})

    # remover duplicatas por (i,z)
    seen = set()
    uniq = []
    for s in sweeps:
        key = (s["index"], s["level"])
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    return uniq

# ------------------- NÍVEL INTERMEDIÁRIO -------------------

def detect_choch(df: pd.DataFrame) -> bool:
    if df is None or len(df) < 3:
        return False

    highs = df['high']
    lows  = df['low']
    closes= df['close']

    # precisa de pelo menos 2 swings na direção original antes do CHOCH
    # ex.: dois higher highs antes de um lower low, ou dois lower lows antes de um higher high
    # aqui simplificamos contando pivôs:
    highs_idx = [i for i in range(1, len(df)) if closes.iat[i] > highs.iloc[:i].max()]
    lows_idx  = [i for i in range(1, len(df)) if closes.iat[i] < lows .iloc[:i].min()]
    up = bool(highs_idx)   # já viu BOS up
    dn = bool(lows_idx)    # já viu BOS down
    return up and dn

def detect_inducement(df: pd.DataFrame, zones: list[float]) -> list[dict]:
    """
    Inducement = sweep falso seguido de candle que volta para o mesmo lado de z.
    Retorna list de {"sweep":sweep, "confirm_idx":i+1}.
    """
    sweeps = detect_liquidity_sweep(df, zones)
    inducements = []

    for sw in sweeps:
        idx, z, dir_ = sw["index"], sw["level"], sw["direction"]
        nxt = idx + 1
        if nxt < len(df):
            c = df['close'].iat[nxt]
            # se sweep up mas fechou acima de z novamente => indução de compras
            if dir_ == "up" and c > z:
                inducements.append({"sweep":sw, "confirm_idx":nxt})
            # se sweep down mas fechou abaixo de z => indução de vendas
            if dir_ == "down" and c < z:
                inducements.append({"sweep":sw, "confirm_idx":nxt})

    return inducements

def detect_premium_discount(df):
    """Premium/Discount: zona acima/abaixo de 50% do último swing."""
    swing_high = df["high"].max()
    swing_low  = df["low"].min()
    midpoint   = (swing_high + swing_low) / 2
    return {"premium": (midpoint, swing_high), "discount": (swing_low, midpoint)}

def detect_killzones(df, timestamp_column):
    """Kill zones de volatilidade baseada em horário (ex.: abertura NY/LON)."""
    # espera coluna datetime index ou coluna de timestamps
    tz = df.index.tz or None
    kills = []
    for ts in df.index:
        hour = ts.hour
        # exemplo: 8-10h (Londres) e 13-15h (NY)
        if (8 <= hour < 10) or (13 <= hour < 15):
            kills.append(ts)
    return kills

# ------------------- EXECUÇÃO E CONTEXTO -------------------

def is_continuation_valid(df):
    """Validação de continuação baseada em BOS + pullback em discount."""
    if not detect_bos(df):
        return False
    pdz = detect_premium_discount(df)["discount"]
    last_close = df["close"].iloc[-1]
    return pdz[0] <= last_close <= pdz[1]

def is_reversal_valid(df):
    """Validação de reversão baseada em CHoCH + inducement."""
    return detect_choch(df) and bool(detect_inducement(df))

