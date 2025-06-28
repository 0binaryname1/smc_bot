import pytest, pandas as pd, numpy as np
from core import patterns

# Fixtures sintéticas para intermediários
@pytest.fixture
def df_inducement():
    # criar candles com sweep falso e confirmação
    data = {'open':[10,12,14,13,12],
            'high':[12,14,16,14,13],
            'low':[9,11,13,12,11],
            'close':[11,13,15,13,14]}
    return pd.DataFrame(data)

@pytest.fixture
def df_premium():
    data = {'open':[1,2,3],'high':[3,4,5],'low':[1,2,3],'close':[2,3,4]}
    return pd.DataFrame(data)

def test_detect_inducement_stub(df_inducement):
    with pytest.raises(NotImplementedError):
        patterns.detect_inducement(df_inducement, zones=[12])

def test_compute_equilibrium_zone_stub(df_premium):
    with pytest.raises(NotImplementedError):
        patterns.compute_equilibrium_zone(df_premium)

def test_detect_killzones_stub(df_premium):
    with pytest.raises(NotImplementedError):
        patterns.detect_killzones(df_premium)

def test_detect_mss_stub(df_premium):
    with pytest.raises(NotImplementedError):
        patterns.detect_mss(df_premium)
