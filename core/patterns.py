# core/patterns.py

"""
Smart Money Concepts (SMC) pattern detection functions.
This module provides basic SMC pattern detection such as Break of Structure (BOS),
Change of Character (CHOCH), Fair Value Gaps (FVG), Order Blocks, liquidity zones, and liquidity sweeps.
"""


import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Any

def detect_bos(df: pd.DataFrame, lookback: int = 2) -> bool:
    """
    Break of Structure (BOS): price close breaks above last swing high (bull) or below last swing low (bear).
    lookback defines how many previous bars to consider for swing calculation.
    """
    if df is None or len(df) < lookback + 1:
        return False

    highs = df['high']
    lows = df['low']
    closes = df['close']

    # swing high/low from lookback bars ago to previous bar
    swing_high = highs.iloc[-(lookback+1):-1].max()
    swing_low = lows.iloc[-(lookback+1):-1].min()
    last_close = closes.iat[-1]

    if last_close > swing_high:
        return True
    if last_close < swing_low:
        return True
    return False


def detect_choch(df: pd.DataFrame) -> bool:
    """
    Change of Character (CHoCH): detecta ao menos um rompimento de alta
    e um rompimento de baixa em sequência, em qualquer ordem, em 2+ barras.
    """
    if df is None or len(df) < 2:
        return False
    highs   = df['high']
    lows    = df['low']
    closes  = df['close']

    # índices onde houve rompimento de swing high ou swing low
    high_breaks = [i for i in range(1, len(df))
                   if closes.iat[i] > highs.iloc[:i].max()]
    low_breaks  = [i for i in range(1, len(df))
                   if closes.iat[i] < lows.iloc[:i].min()]

    # precisa ter ao menos um de cada
    return bool(high_breaks) and bool(low_breaks)

def detect_fvg(df: pd.DataFrame, lookback: int = 3) -> List[Dict[str, Any]]:
    """
    Fair Value Gap: for each window of 3, if candle[i].high < candle[i+2].low => bull gap,
    or candle[i].low > candle[i+2].high => bear gap.
    Returns list of dicts: side, lower, upper, index
    """
    gaps = []
    if df is None or len(df) < lookback:
        return gaps
    highs = df['high']; lows = df['low']
    for i in range(len(df) - 2):
        if highs.iat[i] < lows.iat[i+2]:
            gaps.append({
                'side': 'bull',
                'lower': highs.iat[i],
                'upper': lows.iat[i+2],
                'index': i
            })
        elif lows.iat[i] > highs.iat[i+2]:
            gaps.append({
                'side': 'bear',
                'lower': highs.iat[i+2],
                'upper': lows.iat[i],
                'index': i
            })
    return gaps


def detect_order_blocks(df: pd.DataFrame, min_range: float = 0, lookback: int = 50) -> List[Dict[str, Any]]:
    """
    Detect Order Blocks: last bearish before bullish impulse (bull OB) and vice-versa.
    Returns list of dicts with side, zone (low,high), index of OB candle.
    """
    obs = []
    for i in range(1, min(len(df)-1, lookback)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]
        nxt = df.iloc[i+1]
        # bullish OB: prev bearish and next close > prev.high
        if prev['close'] < prev['open'] and nxt['close'] > prev['high'] and (prev['high']-prev['low']) >= min_range:
            obs.append({'side': 'bull', 'zone': (prev['low'], prev['high']), 'index': i-1})
        # bearish OB: prev bullish and next close < prev.low
        if prev['close'] > prev['open'] and nxt['close'] < prev['low'] and (prev['high']-prev['low']) >= min_range:
            obs.append({'side': 'bear', 'zone': (prev['low'], prev['high']), 'index': i-1})
    # unique by index
    uniq = {o['index']: o for o in obs}
    return list(uniq.values())


def detect_liquidity_zones(df: pd.DataFrame, min_touches: int = 2, tol: float = 1e-5) -> Dict[float,int]:
    counts = {}
    for price in pd.concat([df['high'], df['low']]):
        counts[price] = counts.get(price, 0) + 1
    zones = {}
    for price, cnt in counts.items():
        found = next((z for z in zones if abs(z - price) <= tol), None)
        if found is not None:
            zones[found] += cnt
        else:
            zones[price] = cnt
    return {z: c for z, c in zones.items() if c >= min_touches}


def detect_liquidity_sweep(df: pd.DataFrame, zones: Optional[List[float]] = None,
                           lookback: int = 10, body_ratio: float = 0.5, tol: float = 1e-5) -> List[Dict[str, Any]]:
    """
    Liquidity Sweep: last candle sweeps levels (zones) up or down.
    If zones None, compute on last `lookback` bars.
    Returns list of {'index', 'level', 'direction'}
    """
    if df is None or len(df) < 2:
        return []
    if zones is None:
        recent = df.iloc[-lookback:]
        zones = list(detect_liquidity_zones(recent))
    sweeps = []
    highs = df['high']; lows = df['low']; closes = df['close']; opens = df['open']
    for i in range(1, len(df)):
        h, l, o, c = highs.iat[i], lows.iat[i], opens.iat[i], closes.iat[i]
        rng = h - l
        if rng == 0 or abs(c-o)/rng > body_ratio:
            continue
        for z in zones:
            if h > z + tol and c < z - tol:
                sweeps.append({'index': i, 'level': z, 'direction': 'up'})
            if l < z - tol and c > z + tol:
                sweeps.append({'index': i, 'level': z, 'direction': 'down'})
    # unique
    seen = set()
    uniq = []
    for s in sweeps:
        key = (s['index'], s['level'])
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    return uniq

# ------------------- NÍVEL INTERMEDIÁRIO -------------------

def detect_inducement(df: pd.DataFrame, zones: List[float]) -> List[Dict[str, Any]]:
    """
    Inducement: identifica um sweep seguido de candle de confirmação no mesmo lado.
    - df: DataFrame com colunas ['open','high','low','close']
    - zones: lista de preços de níveis de liquidez (output de detect_liquidity_zones)
    Retorna lista de dicts: {'sweep': {...}, 'confirm_idx': idx_confirm}
    """
    sweeps = detect_liquidity_sweep(df, zones)
    inducements: List[Dict[str, Any]] = []
    for sw in sweeps:
        idx = sw['index']
        z = sw['level']
        dir_ = sw['direction']
        nxt = idx + 1
        if nxt < len(df):
            c = df['close'].iat[nxt]
            if dir_ == 'up' and c > z:
                inducements.append({'sweep': sw, 'confirm_idx': nxt})
            if dir_ == 'down' and c < z:
                inducements.append({'sweep': sw, 'confirm_idx': nxt})
    return inducements


def compute_equilibrium_zone(df: pd.DataFrame) -> Dict[str, tuple]:
    """
    Premium/Discount Zone: calcula swing_high, swing_low e midpoint.
    Retorna dict:
      {'premium': (midpoint, swing_high), 'discount': (swing_low, midpoint)}
    """
    swing_high = df['high'].max()
    swing_low = df['low'].min()
    midpoint = (swing_high + swing_low) / 2
    return {'premium': (midpoint, swing_high), 'discount': (swing_low, midpoint)}


def detect_killzones(df: pd.DataFrame,
                     sessions: List[tuple] = [(8,10), (13,15)]
                    ) -> List[pd.Timestamp]:
    
    #Kill Zones: retorna timestamps cujo hour está nas faixas de volatilidade UTC.
    #sessions: lista de (start_hour, end_hour).
    
    if not hasattr(df, 'index') or not pd.api.types.is_datetime64_any_dtype(df.index):
        raise ValueError("DataFrame deve ter índice datetime para killzones")
    kills: List[pd.Timestamp] = []
    for ts in df.index:
        for start, end in sessions:
            if start <= ts.hour < end:
                kills.append(ts)
                break
    return kills

# ------------------- NÍVEL AVANÇADO -------------------

def detect_mss(df: pd.DataFrame) -> bool:
    """
    Market Structure Shift (MSS): identifica se há pelo menos um BOS e um CHOCH no histórico.
    Retorna True se ambos ocorreram em df.
    """
    return detect_bos(df) and detect_choch(df)


def detect_breaker_blocks(df: pd.DataFrame, min_range: float = 0) -> List[Dict[str, Any]]:
    """
    Breaker Blocks: zonas que resultam de falso rompimento seguido de reversão rápida.
    - df: DataFrame com candles ['open','high','low','close']
    - min_range: range mínimo de candle para considerar.
    Retorna lista de dicts: {'index': i, 'type':'bullish'/'bearish', 'zone':(low,high)}
    """
    blocks: List[Dict[str, Any]] = []
    for i in range(1, len(df)-1):
        prev, curr, nxt = df.iloc[i-1], df.iloc[i], df.iloc[i+1]
        # bearish breaker: curr rompe abaixo do prev.low e próximo fecha acima de curr.high
        if curr['low'] < prev['low'] and nxt['close'] > curr['high'] and (curr['high']-curr['low']) >= min_range:
            blocks.append({'index': i, 'type': 'bearish', 'zone': (curr['low'], curr['high'])})
        # bullish breaker: curr rompe acima do prev.high e próximo fecha abaixo de curr.low
        if curr['high'] > prev['high'] and nxt['close'] < curr['low'] and (curr['high']-curr['low']) >= min_range:
            blocks.append({'index': i, 'type': 'bullish', 'zone': (curr['low'], curr['high'])})
    # remover duplicatas por índice
    seen = set()
    uniq = []
    for b in blocks:
        if b['index'] not in seen:
            seen.add(b['index'])
            uniq.append(b)
    return uniq


def detect_confluence_zones(df: pd.DataFrame, tolerance: float = 1e-5) -> List[float]:
    """
    Confluence Zones: preços onde ocorrem múltiplos padrões simultaneamente.
    - Integrar níveis de Order Blocks, Fair Value Gaps e Liquidity Zones.
    - tolerance: proximidade para agrupar valores.
    Retorna lista de níveis de confluência.
    """
    # coletar níveis de cada padrão
    ob_levels = [lvl for ob in detect_order_blocks(df) for lvl in ob['zone']]
    fvg_levels = [edge for gap in detect_fvg(df) for edge in (gap['lower'], gap['upper'])]
    liq_levels = list(detect_liquidity_zones(df).keys())

    all_levels = ob_levels + fvg_levels + liq_levels
    confluence = []
    for lvl in all_levels:
        # agrupar níveis próximos
        group = [x for x in all_levels if abs(x - lvl) <= tolerance]
        if len(group) >= 2 and not any(abs(c - lvl) <= tolerance for c in confluence):
            confluence.append(lvl)
    return confluence

def detect_mitigation_blocks(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Mitigation Blocks: identifica zonas onde houve "failure swing" seguido de retorno.
    Critério: candle i-1 fecha além de candle i-2 (break), e candle i fecha dentro do range de i-2.
    Retorna lista de dicts: {'index': i, 'type':'bullish'/'bearish', 'zone':(low,high)}
    """
    blocks = []
    for i in range(2, len(df)):
        prev2 = df.iloc[i-2]
        prev1 = df.iloc[i-1]
        curr  = df.iloc[i]
        # bullish mitigation: prev1.high > prev2.high e curr.close <= prev2.high
        if prev1['high'] > prev2['high'] and curr['close'] <= prev2['high']:
            blocks.append({'index': i, 'type': 'bullish', 'zone': (prev2['low'], prev2['high'])})
        # bearish mitigation: prev1.low < prev2.low e curr.close >= prev2.low
        if prev1['low'] < prev2['low'] and curr['close'] >= prev2['low']:
            blocks.append({'index': i, 'type': 'bearish', 'zone': (prev2['low'], prev2['high'])})
    return blocks


def detect_liquidity_voids(df: pd.DataFrame, tol: float = 0.0) -> List[Dict[str, Any]]:
    """
    Liquidity Voids: gaps entre candles sem overlap de preço.
    gap up: curr.low > prev.high + tol
    gap down: curr.high < prev.low - tol
    Retorna lista de {'index', 'type', 'zone'}
    """
    voids = []
    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]
        # gap up
        if curr['low'] > prev['high'] + tol:
            voids.append({'index': i, 'type': 'bullish', 'zone': (prev['high'], curr['low'])})
        # gap down
        if curr['high'] < prev['low'] - tol:
            voids.append({'index': i, 'type': 'bearish', 'zone': (curr['high'], prev['low'])})
    return voids


def detect_stop_hunts(df: pd.DataFrame, wick_ratio: float = 0.5) -> List[int]:
    hunts = []
    for i in range(1, len(df)):
        o, h, l, c = df.iloc[i][['open','high','low','close']]
        rng = h - l
        if rng == 0: continue
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        if lower_wick / rng > wick_ratio and c <= o: hunts.append(i)
        if upper_wick / rng > wick_ratio and c >= o: hunts.append(i)
    return hunts

def detect_multi_fvg(df: pd.DataFrame, min_gaps: int = 2) -> List[tuple]:
    """
    Fair Value Gaps Múltiplos: detecta quando existem pelo menos `min_gaps` gaps.
    Usa detect_fvg internamente.
    Retorna lista de gaps (low, high).
    """
    gaps = detect_fvg(df)
    return gaps if len(gaps) >= min_gaps else []

def detect_order_flow_imbalance(df: pd.DataFrame, factor: float = 2.0) -> List[int]:
    """
    Order Flow Imbalance: identifica candles cujo range > factor * média de ranges.
    (Proxy usando OHLC; para maior precisão, incorpore volume ou dados de livro de ordens.)
    Retorna lista de índices.
    """
    ranges = df['high'] - df['low']
    max_range = ranges.max()
    threshold = factor * max_range

    imbalances: List[int] = []
    for i, r in enumerate(ranges):
        if r > threshold:
            imbalances.append(i)
    return imbalances
