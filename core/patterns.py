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

def detect_bos(df):
    highs = df["high"].tolist()
    lows = df["low"].tolist()
    prev_high = sorted(highs[:-1])[-1]
    prev_low = sorted(lows[:-1])[-1]
    return highs[-1] > prev_high and lows[-1] > prev_low

def detect_order_blocks(df):
    blocks = []
    for i in range(1, len(df)):
        if (df["close"].iloc[i] > df["open"].iloc[i] and df["close"].iloc[i-1] < df["open"].iloc[i-1]) or \
           (df["close"].iloc[i] < df["open"].iloc[i] and df["close"].iloc[i-1] > df["open"].iloc[i-1]):
            blocks.append((df["low"].iloc[i-1], df["high"].iloc[i-1]))
    return blocks

def detect_fvg(df):
    gaps = []
    for i in range(2, len(df)):
        high_prev2 = df["high"].iloc[i-2]
        low_prev1 = df["low"].iloc[i-1]
        if low_prev1 > high_prev2:
            gaps.append((high_prev2, low_prev1))
    return gaps

import numpy as np

def detect_liquidity_zones(df, min_touches=2, tolerance=0.0005):
    """
    Liquidity Zones com tolerância dinâmica.
    
    :param min_touches: Mínimo de toques iguais para validar zona.
    :param tolerance: Tolerância percentual (ex: 0.0005 = 0.05%) entre preços para serem considerados iguais.
    :return: lista de preços médios das zonas de liquidez identificadas.
    """
    highs = df["high"].values
    lows = df["low"].values

    zones = []

    # Avalia highs
    unique_highs = sorted(set(highs), reverse=True)
    for high in unique_highs:
        count = np.sum(np.abs(highs - high) <= high * tolerance)
        if count >= min_touches:
            zones.append(high)

    # Avalia lows
    unique_lows = sorted(set(lows))
    for low in unique_lows:
        count = np.sum(np.abs(lows - low) <= low * tolerance)
        if count >= min_touches:
            zones.append(low)

    return sorted(zones)

def detect_liquidity_sweep(df, zones, body_ratio=0.7, tolerance=0.0005):
    """
    Detecta Liquidity Sweeps com confirmação de candle parcial ou total.
    
    :param zones: Lista de preços médios identificados como Liquidity Zones.
    :param body_ratio: Razão mínima do corpo do candle em relação ao seu range para ser considerado agressivo.
    :param tolerance: Tolerância percentual para considerar toque na zona.
    :return: lista de índices onde ocorreu o liquidity sweep.
    """
    sweeps = []
    for i in range(len(df)):
        candle_range = df["high"].iloc[i] - df["low"].iloc[i]
        body_size = abs(df["close"].iloc[i] - df["open"].iloc[i])

        for zone in zones:
            upper_limit = zone * (1 + tolerance)
            lower_limit = zone * (1 - tolerance)

            if (df["high"].iloc[i] > upper_limit or df["low"].iloc[i] < lower_limit) and (body_size >= candle_range * body_ratio):
                sweeps.append(i)
                break

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

