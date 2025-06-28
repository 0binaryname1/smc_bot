import pandas as pd
import numpy as np
import pytest
from core.patterns import (
    detect_mss,
    detect_breaker_blocks,
    detect_confluence_zones
)


def test_detect_mss_true():
    # BOS at idx1 and CHOCH at idx2: terceira barra fecha abaixo da mínima anterior para gerar CHOCH
    df = pd.DataFrame({
        'open':  [1, 2, 3],
        'high':  [2, 3, 4],
        'low':   [1, 1, 2],
        # idx2 fecha abaixo de 1
        'close': [2, 3, 0],
    })
    # verifica que detect_mss retorna True
    assert detect_mss(df) is True


def test_detect_mss_false():
    # Only BOS, no CHOCH
    df = pd.DataFrame({
        'open':  [1,2,3],
        'high':  [2,3,4],
        'low':   [1,2,3],
        'close': [2,3,4],
    })
    assert detect_mss(df) is False


def test_detect_breaker_blocks_bearish():
    # curr low < prev low, next close > curr.high
    df = pd.DataFrame({
        'open':  [95, 92, 90],
        'high':  [100,105,110],
        'low':   [90, 85, 88],
        'close': [92, 90, 106],
    })
    blocks = detect_breaker_blocks(df)
    assert isinstance(blocks, list)
    assert blocks, "Nenhum breaker block detectado"
    b = blocks[0]
    assert b['type'] == 'bearish'
    assert np.isclose(b['zone'][0], 85) and np.isclose(b['zone'][1], 105)


def test_detect_breaker_blocks_bullish():
    # curr high > prev high, next close < curr.low
    df = pd.DataFrame({
        'open':  [95, 98, 100],
        'high':  [100,110,105],
        'low':   [90,  95,  93],
        'close': [98, 100, 93],
    })
    blocks = detect_breaker_blocks(df)
    assert isinstance(blocks, list)
    assert blocks, "Nenhum breaker block detectado"
    b = blocks[0]
    assert b['type'] == 'bullish'
    assert np.isclose(b['zone'][0], 95) and np.isclose(b['zone'][1], 110)


def test_detect_confluence_zones():
    # Cenário sem confluência real quando apenas breaker blocks existem
    df = pd.DataFrame({
        'open':  [95, 92, 90, 85],
        'high':  [100,105,110,115],
        'low':   [90,  85,  88,  87],
        'close': [92,  90, 106,  112],
    })
    blocks = detect_breaker_blocks(df)
    conflate = detect_confluence_zones(df)
    assert isinstance(conflate, list)
    # sem confluência pois só há um tipo de padrão
    assert conflate == []
