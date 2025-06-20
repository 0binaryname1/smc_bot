# core/patterns.py

"""
Módulos SMC - patterns.py
Detectores de padrões SMC divididos por nível
"""

from .config import (
    LIQUIDITY_MIN_TOUCHES,
    LIQUIDITY_TOLERANCE,
    SWEEP_BODY_RATIO,
    SWEEP_PARTIAL_MARGIN,
)

# ------------------- NÍVEL BÁSICO -------------------

import numpy as np 
import pandas as pd

def detect_fvg(df: pd.DataFrame) -> list[tuple[int, float]]:
    """ Fair Value Gaps: quando o close de uma vela ├⌐ maior que o high da vela anterior. Retorna lista de (├¡ndice_da_vela_anterior, close_da_vela_atual). """ 
    gaps: list[tuple[int, float]] = []
    for i in range(1, len(df)): 
        prev_high = float(df.iloc[i-1]["high"]) 
        curr_close = float(df.iloc[i]["close"]) 
        if curr_close > prev_high: 
            gaps.append((i-1, curr_close)) 
    return gaps

def detect_order_blocks(df: pd.DataFrame) -> list[tuple[float, float]]: 
    """ Order blocks simples: marca sempre a primeira e a ├║ltima vela do df. Retorna lista de (low, high) dessas velas. """ 
    blocks: list[tuple[float, float]] = [] 
    for i in (0, len(df)-1): 
        low = float(df.iloc[i]["low"]) 
        high = float(df.iloc[i]["high"]) 
        blocks.append((low, high)) 
    return blocks

def detect_liquidity_zones( 
    df: pd.DataFrame, 
    min_touches: int = 2, 
    tolerance: float = 0.0005 
) -> list[float]: 
    """ Agrupa highs e lows que se repetem pelo menos min_touches vezes dentro de uma toler├óncia, devolvendo o n├¡vel m├⌐dio de cada zona. """ 
    levels = list(df["low"]) + list(df["high"]) 
    clusters: list[list[float]] = [] 
    for lvl in levels: 
        placed = False 
        for cl in clusters:
            if abs(float(lvl) - cl[0]) <= tolerance: 
                cl.append(float(lvl)) 
                placed = True 
                break 
        if not placed: 
            clusters.append([float(lvl)]) 
    zones = [sum(cl)/len(cl) for cl in clusters if len(cl) >= min_touches] 
    return zones

def detect_liquidity_sweep(
        df: pd.DataFrame, 
        zones: list[float], 
        body_ratio: float = 0.7, 
        tolerance: float = 0.0005 
) -> list[int]: 
    """ Identifica candles que ΓÇ£varremΓÇ¥ (sweep) uma zona de liquidez: wick ultrapassa a zone+tolerance e propor├º├úo corpo/total < body_ratio. Retorna lista de ├¡ndices dos candles varredores. """ 
    sweeps: list[int] = [] 
    for i, row in df.iterrows(): 
        high, low = float(row["high"]), float(row["low"]) 
        o, c = float(row["open"]), float(row["close"]) 
        body = abs(c - o) 
        total = high - low 
        if total == 0: 
            continue 
        if any(high >= zone + tolerance for zone in zones): 
            if (body / total) < body_ratio: 
                sweeps.append(i) 
    return sweeps

# ------------------- NÍVEL INTERMEDIÁRIO -------------------

def detect_choch(df):
    """Change of Character (CHoCH): primeiro rompimento contra tendência anterior."""
    highs = df["high"].tolist()
    lows  = df["low"].tolist()
    # usa últimos 3 pivôs para definir CHoCH
    if len(highs) < 4:
        return False
    # detecta fundo mais baixo em alta vigente ou topo mais alto em baixa vigente
    return lows[-1] < lows[-2] and highs[-2] > highs[-3] or highs[-1] > highs[-2] and lows[-2] < lows[-3]

def detect_inducement(df):
    """Indução: rompimento falso de liquidity zone seguido de volta rápida."""
    sweeps = detect_liquidity_sweep(df)
    zones  = detect_liquidity_zones(df)
    inducements = []
    for idx in sweeps:
        # logo após sweep, fechar de volta dentro da zona
        if idx+1 < len(df):
            if df["low"].iloc[idx+1] >= min(zones, default=0) and df["high"].iloc[idx+1] <= max(zones, default=0):
                inducements.append(idx)
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

