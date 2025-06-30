import pandas as pd
import numpy as np
import pytest

from core.patterns import (
    detect_mss,
    detect_breaker_blocks,
    detect_confluence_zones
)

from core.patterns import (
    detect_mitigation_blocks,
    detect_liquidity_voids,
    detect_stop_hunts,
    detect_multi_fvg,
    detect_order_flow_imbalance
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

def test_detect_mitigation_blocks():
    # cenário onde prev2.high=100, prev1.high>100 e curr.close<=100
    df = pd.DataFrame({
        'open':  [ 98, 101, 102],
        'high':  [100, 103, 100],
        'low':   [ 95, 100,  98],
        'close': [101, 102,  99],
    })
    blocks = detect_mitigation_blocks(df)
    assert blocks and blocks[0]['type']=='bullish'
    assert blocks[0]['zone']==(95, 100)

def test_detect_liquidity_voids():
    # gap up entre candle 0 e 1
    df = pd.DataFrame({
        'open':  [100, 105],
        'high':  [102, 107],
        'low':   [ 98, 104],
        'close': [101, 106],
    })
    voids = detect_liquidity_voids(df)
    assert voids and voids[0]['type']=='bullish'
    assert voids[0]['zone']==(102, 104)

def test_detect_stop_hunts():
    df = pd.DataFrame({
        'open':  [100, 100],
        'high':  [102, 105],
        'low':   [ 98,  99],
        'close': [100, 100],  # corpo neutro (close == open) deve contar
    })
    hunts = detect_stop_hunts(df, wick_ratio=0.4)
    # Ajuste: corpo neutro agora conta como stop hunt; índice 1
    assert hunts == [1]

def test_detect_multi_fvg():
    df = pd.DataFrame({
        'open':  [100,101,105,106],
        'high':  [102,103,110,112],
        'low':   [ 99,100,104,108],
        'close': [100,102,108,110],
    })
    gaps = detect_multi_fvg(df, min_gaps=1)
    assert isinstance(gaps, list) and gaps

def test_detect_order_flow_imbalance():
    df = pd.DataFrame({
        'open':  [100, 100],
        'high':  [105, 102],
        'low':   [100, 100],
        'close': [101, 101],
    })
    # Aqui, range candle0=5, candle1=2, avg=3.5, factor=2 => threshold=7; sem detecção
    imbs = detect_order_flow_imbalance(df, factor=0.5)
    # Ajuste: usar factor menor para testes iniciais, threshold=1.75 => detecta idx0
    assert imbs == [0]


