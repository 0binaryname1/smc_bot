import pytest
import pandas as pd
import numpy as np
from core.patterns import (
    detect_inducement,
    compute_equilibrium_zone,
    detect_killzones
)

# Fixtures sintéticas para intermediários
@pytest.fixture
def df_inducement():
    # construir candles com sweep real e confirmação de indução
    # sweep up (último candle rompe acima de zone 100) e fecha abaixo para inducer up
    data = {
        'open':  [98, 99, 100, 100],
        'high':  [99,100, 102, 102],
        'low':   [97, 98,   99, 100],
        # idx 2 fecha abaixo de 100 (sweep), idx 3 fecha acima para confirmar
        'close': [99,100,  99, 101],
    }
    # último candle fecha acima de 100 confirmando indução
    df = pd.DataFrame(data)
    # índices de sweep up no idx=2, zone=100
    return df, [100]

@pytest.fixture
def df_premium():
    data = {'open': [1,2,3], 'high': [3,4,5], 'low': [1,2,3], 'close': [2,3,4]}
    return pd.DataFrame(data)

@pytest.fixture
def df_killzones():
    rng = pd.date_range('2025-06-28 07:00', periods=10, freq='H', tz='UTC')
    df = pd.DataFrame({'open': range(10), 'high': range(1,11), 'low': range(1,11), 'close': range(1,11)}, index=rng)
    return df


def test_detect_inducement(df_inducement):
    df, zones = df_inducement
    res = detect_inducement(df, zones)
    assert isinstance(res, list)
    assert res and res[0]['confirm_idx'] == 3


def test_compute_equilibrium_zone(df_premium):
    zones = compute_equilibrium_zone(df_premium)
    assert 'premium' in zones and 'discount' in zones
    hi = df_premium['high'].max(); lo = df_premium['low'].min()
    mid = (hi+lo)/2
    assert zones['premium'] == (mid, hi)
    assert zones['discount'] == (lo, mid)


def test_detect_killzones(df_killzones):
    kills = detect_killzones(df_killzones)
    # sessões 8-10 e 13-15 UTC => índices com hour 8,9,13,14
    hrs = [ts.hour for ts in kills]
    for h in [8,9,13,14]:
        assert h in hrs

