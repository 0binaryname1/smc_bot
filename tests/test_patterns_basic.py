import pandas as pd
import pytest
from core.patterns import (
    detect_bos,
    detect_order_blocks,
    detect_fvg,
    detect_liquidity_zones,
    detect_liquidity_sweep
)

@pytest.fixture
def df_bos():
    return pd.DataFrame({
        "open":  [1, 2, 3, 4, 5],
        "high":  [2, 3, 4, 5, 7],
        "low":   [0.5, 1.5, 2.5, 3.5, 4.5],
        "close": [1.8, 2.8, 3.8, 4.8, 6.8],
    })

def test_detect_bos_true(df_bos):
    # esperamos que o último candle gere um BOS de alta
    assert detect_bos(df_bos) is True

def test_detect_bos_false():
    # um mercado lateral sem rompimento
    df = pd.DataFrame({
        "open":  [1, 1, 1],
        "high":  [2, 2, 2],
        "low":   [0.5, 0.5, 0.5],
        "close": [1.5, 1.5, 1.5],
    })
    assert detect_bos(df) is False

def test_detect_fvg():
    df_fvg = pd.DataFrame({
        "open":  [1, 2],
        "high":  [2, 3],
        "low":   [1, 2],
        "close": [2, 4],
    })
    # só há gap (close > high) na segunda vela: low=2, close=4
    expected = [(0, 4)]
    result = detect_fvg(df_fvg)
    assert result == expected

def test_detect_order_blocks():
    df = pd.DataFrame({
        "open": [1, 2, 1, 2],
        "high": [2, 3, 2, 4],
        "low": [0.5, 1.5, 0.8, 1.2],
        "close": [2, 1.8, 1.9, 1.5],
    })
    # esperamos os "order blocks" na primeira e na última vela
    expected = [(0.5, 2), (1.2, 4)]
    result = detect_order_blocks(df)

    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        assert np.allclose(r, e), f"Mismatch: got {r}, expected {e}"

def test_detect_liquidity_zones():
    df = pd.DataFrame({
        "high": [1.1000, 1.1003, 1.0998, 1.1050],
        "low": [1.0900, 1.0901, 1.0899, 1.0850]
    })
    zones = detect_liquidity_zones(df, min_touches=2, tolerance=0.0005)
    assert len(zones) == 2
    assert 1.1000 in zones or 1.1003 in zones
    assert 1.0900 in zones or 1.0901 in zones

def test_detect_liquidity_sweep():
    df = pd.DataFrame({
        "open": [1.1000, 1.1005],
        "high": [1.1003, 1.1060],
        "low": [1.0995, 1.1000],
        "close": [1.1002, 1.1010]
    })
    zones = [1.1003]
    sweeps = detect_liquidity_sweep(df, zones, body_ratio=0.7, tolerance=0.0005)
    assert len(sweeps) == 1
    assert sweeps[0] == 1

