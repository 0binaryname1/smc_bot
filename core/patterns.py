# core/patterns.py

"""
Smart Money Concepts (SMC) pattern detection functions.
This module provides basic SMC pattern detection such as Break of Structure (BOS),
Change of Character (CHOCH), Fair Value Gaps (FVG), Order Blocks, liquidity zones, and liquidity sweeps.
"""

import numpy as np
import pandas as pd

def detect_bos(df: pd.DataFrame) -> bool:
    """
    Detects a Break of Structure (BOS) in the provided price data.
    A BOS occurs when price breaks the previous significant high (for bullish BOS) 
    or the previous significant low (for bearish BOS).
    
    Basic implementation: returns True if the last candle's high is higher than any prior high (bullish BOS)
    or the last candle's low is lower than any prior low (bearish BOS), indicating a structural break. 
    Otherwise returns False.
    """
    if df is None or df.empty:
        return False
    highs = df['high']
    lows = df['low']
    last_high = highs.iloc[-1]
    last_low = lows.iloc[-1]
    # Check if last high breaks above all previous highs (bullish BOS)
    if last_high > highs[:-1].max():
        return True
    # Check if last low breaks below all previous lows (bearish BOS)
    if last_low < lows[:-1].min():
        return True
    return False

def detect_choch(df: pd.DataFrame) -> bool:
    """
    Detects a Change of Character (CHOCH) in the provided price data.
    A CHOCH is typically identified when the market, which had been trending in one direction,
    breaks structure in the opposite direction, indicating a potential trend reversal.
    
    Basic implementation: returns True if both a bullish and bearish break of structure 
    are detected in the price series. 
    """
    if df is None or df.empty:
        return False
    highs, lows = df['high'], df['low']
    # find all break points
    ups = [i for i in range(1, len(df) if highs.iloc[i] > highs.iloc[:i].max()]
    downs = [i for i in range(1, len(df)) if lows.iloc[i] < lows.iloc[:i].min()]
           return bool(ups and downs)   

def detect_fvg(df: pd.DataFrame) -> list:
    """
    Detects Fair Value Gaps (FVG) in the provided price data.
    A fair value gap is a price range between two consecutive candles where the second candle does not overlap 
    the first candle's range, leaving a 'gap' in price action.
    
    Returns a list of tuples for each detected gap. Each tuple is (gap_lower_price, gap_upper_price).
    """
    gaps = []
    if df is None or len(df) < 2:
        return gaps
    for i in range(1, len(df)):
           prev_h, prev_1 = df['high'].iat[i-1], df['low'].iat[i-1]
           curr_c = df['close'].iat[i]
           if curr_c > prev_h: 
                gaps.append((i-1, curr_c))
           eliff curr_c < prev_1:
               gaps.append(i-1, curr_c))
    return gaps

def detect_order_blocks(df: pd.DataFrame) -> list:
    """
    Detects Order Blocks in the provided price data.
    An Order Block is typically the last opposing candle (bullish or bearish) before a significant move (BOS).
    For simplicity, this function identifies potential order blocks by finding large candles preceding a break of structure.
    
    Returns a list of indices of candles that could be order blocks.
    """
    order_blocks = []
    if df is None or len(df) < 3:
        return order_blocks
    highs = df['high']
    lows = df['low']
    closes = df['close']
    opens = df['open']
    # Identify break of structure points (both up and down)
    current_max = highs.iloc[0]
    current_min = lows.iloc[0]
    bos_indices = []
    bos_directions = []  # 'up' or 'down'
    for i in range(1, len(df)):
        if highs.iloc[i] > current_max:
            bos_indices.append(i)
            bos_directions.append('up')
            current_max = highs.iloc[i]
        if lows.iloc[i] < current_min:
            bos_indices.append(i)
            bos_directions.append('down')
            current_min = lows.iloc[i]
    # Determine order blocks: if BOS up, previous candle if bearish; if BOS down, previous candle if bullish
    for idx, direction in zip(bos_indices, bos_directions):
        prev_idx = idx - 1
        if prev_idx >= 0:
            if direction == 'up':
                # bullish BOS -> previous bearish candle might be an order block
                if closes.iloc[prev_idx] < opens.iloc[prev_idx]:
                    order_blocks.append(prev_idx)
            elif direction == 'down':
                # bearish BOS -> previous bullish candle might be an order block
                if closes.iloc[prev_idx] > opens.iloc[prev_idx]:
                    order_blocks.append(prev_idx)
    # Remove duplicates and sort
    order_blocks = sorted(set(order_blocks))
    return order_blocks

def detect_liquidity_zones(df, min_touches=2, tolerance=1e-8):
    """
    Detects liquidity zones (areas of equal highs or equal lows) in the provided price data.
    These zones indicate potential liquidity (stop orders) resting above equal highs or below equal lows.
    
    Basic implementation: returns a list of price levels that appear at least twice as highs or at least twice as lows.
    Uses a tolerance to account for floating point differences.
    """
    if df is None or df.empty:
        return []
    prices = pd.concat([df['high'], df['low']]).values
    zones = []
    used = set()
    for p in prices:
        if any(abs(p-z) <= tolerance for z in used):
            continue
        count = sum(abs(prices - p) <= tolerance)
        if count >= min_touches:
            zones.append(float(p))
            used.add(p)
    return sorted(zones)

def detect_liquidity_sweep(df, zones, boddy_ratio=0.7, tolerance=1e-8):
    """
    Detects liquidity sweeps in the provided price data.
    A liquidity sweep occurs when price moves beyond a previous swing high (or low), 
    taking out liquidity, but then reverses (closes back below the broken high or above the broken low).
    
    Basic implementation: returns a list of price levels that were swept.
    For each candle that makes a new high above all previous highs but closes below that previous high level, 
    the previous high level is recorded as a swept liquidity level.
    Similarly for new lows that close above the previous low level.
    """
    sweeps = set()
    if df is None or len(df) < 2:
        return []
    o, h, l, c = df['open'], df['high'], df['low'], df['close']
    for i in range(1, len(df)):
        body = abs(o.iat[i] - c.iat[i])
        rng = h.iat[i] - l.iat[i]
        if rng <= 0:
            continue
        for z in zones:
            if h.iat[i] > z + tolerance and c.iat[i] < z - tolerance:
                sweeps.add(i)
    return sorted(sweeps)

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

