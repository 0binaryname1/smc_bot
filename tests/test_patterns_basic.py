import numpy as np
import pandas as pd
import pytest

from core.patterns import (
    detect_bos,
    detect_choch,
    detect_fvg,
    detect_order_blocks,
    detect_liquidity_zones,
    detect_liquidity_sweep,
)

# -------------------------------------
#  TESTES BÁSICOS REFATORADOS
# -------------------------------------

def test_detect_bos_no_break():
    df = pd.DataFrame({'open':[1,4,5],'high':[5,6,4],'low':[1,3,2],'close':[4,5,3]})
    assert detect_bos(df) is False

def test_detect_bos_bullish():
    df = pd.DataFrame({'open':[1,2,3],'high':[5,6,7],'low':[0,1,2],'close':[4,5,8]})
    assert detect_bos(df) is True

def test_detect_bos_bearish():
    df = pd.DataFrame({'open':[5,4,3],'high':[6,5,4],'low':[2,3,1],'close':[5,4,0]})
    assert detect_bos(df) is True

def test_detect_choch_no_change():
    df = pd.DataFrame({'open':[1,2,3,4],'high':[5,6,7,8],'low':[1,2,3,4],'close':[4,5,6,7]})
    assert detect_choch(df) is False

def test_detect_choch_up_then_down():
    df = pd.DataFrame({'open':[5,5,5],'high':[10,12,11],'low':[5,5,4],'close':[9,11,3]})
    assert detect_choch(df) is True

def test_detect_choch_down_then_up():
    df = pd.DataFrame({'open':[10,10,10],'high':[15,14,16],'low':[5,3,3],'close':[9,4,17]})
    assert detect_choch(df) is True

def test_detect_fvg_gaps():
    # Fair Value Gap requer 3 candles: idx 0->2 gap
    df_up = pd.DataFrame({
        'open':  [100, 101, 105],
        'high':  [102, 103, 110],
        'low':   [ 99, 100, 105],
        'close': [100, 102, 108],
    })
    df_dn = pd.DataFrame({
        'open':  [50, 49, 45],
        'high':  [55, 52, 48],
        'low':   [49, 48, 40],
        'close': [49, 50, 42],
    })

    expected_up = [{'side': 'bull', 'lower': 102.0, 'upper': 105.0, 'index': 0}]
    expected_dn = [{'side': 'bear', 'lower': 48.0,  'upper': 49.0,  'index': 0}]
    result_up = detect_fvg(df_up)
    result_dn = detect_fvg(df_dn)

    assert result_up == expected_up
    assert result_dn == expected_dn

def test_detect_order_blocks_basic():
    df = pd.DataFrame({
        'open':[100,98,105,106],
        'high':[105,110,108,107],
        'low':[95,97,104,90],
        'close':[98,109,107,95],
    })
    obs = detect_order_blocks(df)
    assert isinstance(obs, list)
    idxs = [o['index'] for o in obs]
    assert 0 in idxs

def test_detect_liquidity_zones_basic():
    df = pd.DataFrame({
        'open':[10,11,12,13],
        'high':[20,20,25,18],
        'low':[5,4,4,7],
        'close':[15,19,24,10],
    })
    zones = detect_liquidity_zones(df)
    assert isinstance(zones, dict)
    assert any(np.isclose(z,4.0) for z in zones)
    assert any(np.isclose(z,20.0) for z in zones)

def test_detect_liquidity_sweep_signature_and_type():
    df = pd.DataFrame({'open':[100,101],'high':[100,105],'low':[95,95],'close':[100,98]})
    zones = list(detect_liquidity_zones(df))
    result = detect_liquidity_sweep(df, zones)
    assert isinstance(result, list)
