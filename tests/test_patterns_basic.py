import pandas as pd
import numpy as np
from core import patterns

def test_detect_bos_no_break():
    # Cria dados onde o último candle NÃO rompe máximas/mínimas estruturais anteriores
    df = pd.DataFrame({
        "open": [1, 4, 5],
        "high": [5, 6, 4],
        "low":  [1, 3, 2],
        "close":[4, 5, 3]
    })
    # Último candle (índice 2): high=4 não supera max anterior=6; low=2 não cai abaixo min anterior=1.
    # Portanto, não houve BOS.
    assert patterns.detect_bos(df) is False

def test_detect_bos_bullish():
    # Último candle faz nova máxima em relação a todos os anteriores -> BOS altista
    df = pd.DataFrame({
        "open": [1, 2, 3],
        "high": [5, 6, 7],
        "low":  [0, 1, 2],
        "close":[4, 5, 6]
    })
    # High final 7 > high máximo anterior (6) => deve detectar BOS
    assert patterns.detect_bos(df) is True

def test_detect_bos_bearish():
    # Último candle faz nova mínima em relação a todos os anteriores -> BOS baixista
    df = pd.DataFrame({
        "open": [5, 4, 3],
        "high": [6, 5, 4],
        "low":  [2, 3, 1],
        "close":[5, 4, 2]
    })
    # Low final 1 < low mínimo anterior (2) => deve detectar BOS
    assert patterns.detect_bos(df) is True

def test_detect_choch_no_change():
    # Mercado tendendo apenas em alta (somente BOS altistas, nenhum BOS baixista) -> sem CHOCH
    df = pd.DataFrame({
        "open": [1, 2, 3, 4],
        "high": [5, 6, 7, 8],   # máximas sempre crescentes (BOS altista contínuo)
        "low":  [1, 2, 3, 4],   # mínimas também sobem, sem romper mínimas anteriores
        "close":[4, 5, 6, 7]
    })
    assert patterns.detect_choch(df) is False

def test_detect_choch_up_then_down():
    # Um BOS altista seguido por um BOS baixista -> caracteriza CHOCH (mudança de tendência de alta para baixa)
    df = pd.DataFrame({
        "open": [5, 5, 5],
        "high": [10, 12, 11],  # índice1 rompe acima de 10 (BOS altista), índice2 não rompe acima de 12
        "low":  [5, 5, 4],     # índice2 rompe abaixo de 5 (BOS baixista)
        "close":[9, 11, 6]
    })
    # Explicação: no índice1 high=12 > max anterior 10 (BOS altista); no índice2 low=4 < min anterior 5 (BOS baixista).
    # Houve rompimento nos dois sentidos -> CHOCH.
    assert patterns.detect_choch(df) is True

def test_detect_choch_down_then_up():
    # Um BOS baixista seguido por um BOS altista -> CHOCH (mudança de tendência de baixa para alta)
    df = pd.DataFrame({
        "open": [10, 10, 10],
        "high": [15, 14, 16],  # índice2 rompe acima de 15 (BOS altista)
        "low":  [5, 3, 3],     # índice1 rompe abaixo de 5 (BOS baixista), índice2 não faz nova mínima
        "close":[9, 4, 15]
    })
    # Explicação: índice1 low=3 < min anterior 5 (BOS baixista); índice2 high=16 > max anterior 15 (BOS altista).
    assert patterns.detect_choch(df) is True

def test_detect_fvg_no_gap():
    # Candles consecutivos com sobreposição total (sem gap)
    df = pd.DataFrame({
        "open": [1,   1.5],
        "high": [2,   2.1],   # máxima do segundo candle (2.1) ainda está acima da máxima do primeiro (2) -> sobrepõe
        "low":  [1,   1.8],   # mínima do segundo (1.8) está acima de 1 e abaixo de 2 -> sobrepõe também
        "close":[1.5, 2]
    })
    result = patterns.detect_fvg(df)
    assert result == []  # não deve haver gaps

def test_detect_fvg_upward_gap():
    # Segundo candle inteiramente acima do range do primeiro -> gap de alta
    df = pd.DataFrame({
        "open": [100, 105],
        "high": [102, 110],
        "low":  [99,  105],   # mínima do candle1 (105) está acima do fechamento do candle0 (100)
        "close":[100, 108]
    })
    # Candle0 fechou a 100, Candle1 mínima 105 -> gap de 100 a 105
    expected = [(100, 105)]
    result = patterns.detect_fvg(df)
    # Compara usando isclose para evitar problemas de ponto flutuante
    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        assert np.isclose(r[0], e[0]) and np.isclose(r[1], e[1])

def test_detect_fvg_downward_gap():
    # Segundo candle inteiramente abaixo do range do primeiro -> gap de baixa
    df = pd.DataFrame({
        "open": [50, 45],
        "high": [55, 48],   # máxima do candle1 (48) está abaixo do fechamento do candle0 (49)
        "low":  [49, 40],
        "close":[49, 42]
    })
    # Candle0 fechou a 49, Candle1 máxima 48 -> gap de 48 a 49
    expected = [(48, 49)]
    result = patterns.detect_fvg(df)
    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        assert np.isclose(r[0], e[0]) and np.isclose(r[1], e[1])

def test_detect_order_blocks_basic():
    # Cenário com um BOS altista e depois um BOS baixista para identificar order blocks:
    # - Candle0 de baixa antes de BOS altista no Candle1 -> candle0 é order block de compra.
    # - Candle2 de alta antes de BOS baixista no Candle3 -> candle2 é order block de venda.
    df = pd.DataFrame({
        "open":  [100,  98, 105, 106],
        "high":  [105, 110, 108, 107],
        "low":   [95,   97, 104,  90],
        "close": [98,  109, 107,  95]
    })
    # Detalhes:
    # Candle0: bearish (open100 > close98)
    # Candle1: bullish (open98 < close109), high110 > high anterior105 (BOS up no idx1). Prev idx0 era bearish -> idx0 marcado.
    # Candle1 também teve low97 < low anterior95 (BOS down no idx1, mas prev idx0 bearish não marca nada para down).
    # Candle2: bullish (open105 < close107), não faz novo high (108 < 110) nem novo low (104 > 95) -> sem BOS.
    # Candle3: bearish (open106 > close95), low90 < low anterior95 (BOS down no idx3). Prev idx2 era bullish -> idx2 marcado.
    expected = [0, 2]
    result = patterns.detect_order_blocks(df)
    assert result == expected

def test_detect_liquidity_zones_basic():
    # Dados com máximas e mínimas duplicadas para formar zonas de liquidez
    df = pd.DataFrame({
        "open":  [10, 11, 12, 13],
        "high":  [20, 20, 25, 18],  # high=20 repete nos índices 0 e 1 -> zona de liquidez em 20
        "low":   [5,  4,  4,  7],   # low=4 repete nos índices 1 e 2 -> zona de liquidez em 4
        "close": [15, 19, 24, 10]
    })
    zones = patterns.detect_liquidity_zones(df)
    # Espera zonas [4, 20] (ordem crescente)
    assert len(zones) == 2
    assert any(np.isclose(z, 4) for z in zones)
    assert any(np.isclose(z, 20) for z in zones)

def test_detect_liquidity_sweep_upward():
    # Liquidity sweep altista: Candle1 rompe acima do topo do Candle0, mas fecha abaixo deste topo
    df = pd.DataFrame({
        "open":  [100, 101],
        "high":  [100, 105],  # Candle1 faz máxima 105 > topo anterior 100
        "low":   [95,  95],
        "close": [100, 98]    # Candle1 fecha em 98, abaixo do topo anterior 100
    })
    sweeps = patterns.detect_liquidity_sweep(df)
    # O topo anterior (100) deve ser identificado como varrido
    assert len(sweeps) == 1
    assert np.isclose(sweeps[0], 100)

def test_detect_liquidity_sweep_downward():
    # Liquidity sweep baixista: Candle1 rompe abaixo do fundo do Candle0, mas fecha acima deste fundo
    df = pd.DataFrame({
        "open":  [50, 49],
        "high":  [60, 55],
        "low":   [50, 45],   # Candle1 faz mínima 45 < fundo anterior 50
        "close": [50, 52]    # Candle1 fecha em 52, acima do fundo anterior 50
    })
    sweeps = patterns.detect_liquidity_sweep(df)
    # O fundo anterior (50) deve ser identificado como varrido
    assert len(sweeps) == 1
    assert np.isclose(sweeps[0], 50)

