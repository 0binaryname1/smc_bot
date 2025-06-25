import numpy as np
import pandas as pd
from core.patterns import (
    detect_bos,
    detect_choch,
    detect_fvg,
    detect_order_blocks,
    detect_liquidity_zones,
    detect_liquidity_sweep,
)

def test_detect_bos_no_break():
    df = pd.DataFrame({
        "open":  [1, 4, 5],
        "high":  [5, 6, 4],
        "low":   [1, 3, 2],
        "close": [4, 5, 3],
    })
    # high=4 ≤ prev max=6; low=2 ≥ prev min=1 → sem BOS
    assert detect_bos(df) is False

def test_detect_bos_bullish():
    df = pd.DataFrame({
        "open":  [1, 2, 3],
        "high":  [5, 6, 7],
        "low":   [0, 1, 2],
        "close": [4, 5, 6],
    })
    # high final 7 > max anterior 6 → BOS altista
    assert detect_bos(df) is True

def test_detect_bos_bearish():
    df = pd.DataFrame({
        "open":  [5, 4, 3],
        "high":  [6, 5, 4],
        "low":   [2, 3, 1],
        "close": [5, 4, 2],
    })
    # low final 1 < min anterior 2 → BOS baixista
    assert detect_bos(df) is True

def test_detect_choch_no_change():
    df = pd.DataFrame({
        "open":  [1, 2, 3, 4],
        "high":  [5, 6, 7, 8],
        "low":   [1, 2, 3, 4],
        "close": [4, 5, 6, 7],
    })
    # só BOS altistas, nunca BOS baixista → sem CHOCH
    assert detect_choch(df) is False

def test_detect_choch_up_then_down():
    df = pd.DataFrame({
        "open":  [5, 5, 5],
        "high":  [10, 12, 11],
        "low":   [5, 5, 4],
        "close": [9, 11, 6],
    })
    # primeiro BOS altista (12>10), depois BOS baixista (4<5) → CHOCH
    assert detect_choch(df) is True

def test_detect_choch_down_then_up():
    df = pd.DataFrame({
        "open":  [10, 10, 10],
        "high":  [15, 14, 16],
        "low":   [5, 3, 3],
        "close": [9, 4, 15],
    })
    # primeiro BOS baixista (3<5), depois BOS altista (16>15) → CHOCH
    assert detect_choch(df) is True

def test_detect_fvg_no_gap():
    df = pd.DataFrame({
        "open":  [1.0, 1.5],
        "high":  [2.0, 2.1],
        "low":   [1.0, 1.8],
        "close": [1.5, 2.0],
    })
    assert detect_fvg(df) == []

def test_detect_fvg_upward_gap():
    df = pd.DataFrame({
        "open":  [100, 105],
        "high":  [102, 110],
        "low":   [99, 105],
        "close": [100, 108],
    })
    # gap de alta: prev_high=102, curr_low=105
    expected = [(102.0, 105.0)]
    result = detect_fvg(df)
    assert len(result) == len(expected)
    for (got0, got1), (exp0, exp1) in zip(result, expected):
        assert np.isclose(got0, exp0)
        assert np.isclose(got1, exp1)

def test_detect_fvg_downward_gap():
    df = pd.DataFrame({
        "open":  [50, 45],
        "high":  [55, 48],
        "low":   [49, 40],
        "close": [49, 42],
    })
    # gap de baixa: curr_high=48, prev_low=49
    expected = [(48.0, 49.0)]
    result = detect_fvg(df)
    assert len(result) == len(expected)
    for (got0, got1), (exp0, exp1) in zip(result, expected):
        assert np.isclose(got0, exp0)
        assert np.isclose(got1, exp1)

def test_detect_order_blocks_basic():
    df = pd.DataFrame({
        "open":  [100,  98, 105, 106],
        "high":  [105, 110, 108, 107],
        "low":   [95,   97, 104,  90],
        "close": [98,  109, 107,  95],
    })
    # espera OB nos índices [0, 2]
    expected = [0, 2]
    result = detect_order_blocks(df)
    assert result == expected

def test_detect_liquidity_zones_basic():
    df = pd.DataFrame({
        "open":  [10, 11, 12, 13],
        "high":  [20, 20, 25, 18],
        "low":   [5,  4,  4,  7],
        "close": [15, 19, 24, 10],
    })
    zones = detect_liquidity_zones(df)
    # espera [4, 20] (ordem irrelevante)
    assert len(zones) == 2
    assert any(np.isclose(z, 4.0) for z in zones)
    assert any(np.isclose(z, 20.0) for z in zones)

def test_detect_liquidity_sweep_upward():
    df = pd.DataFrame({
        "open":  [100, 101],
        "high":  [100, 105],
        "low":   [95,  95],
        "close": [100, 98],
    })
    sweeps = detect_liquidity_sweep(df)
    assert len(sweeps) == 1
    assert np.isclose(sweeps[0], 100.0)

def test_detect_liquidity_sweep_downward():
    df = pd.DataFrame({
        "open":  [50, 49],
        "high":  [60, 55],
        "low":   [50, 45],
        "close": [50, 52],
    })
    sweeps = detect_liquidity_sweep(df)
    assert len(sweeps) == 1
    assert np.isclose(sweeps[0], 50.0)
