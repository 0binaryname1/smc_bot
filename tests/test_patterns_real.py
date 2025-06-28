import glob
import random
from pathlib import Path

import pandas as pd
import pytest

from core import patterns

DATA_DIR = Path(__file__).parents[1] / "data" / "data_assets"
PARQUETS = sorted(DATA_DIR.glob("btc_m1_part*.parquet"))
if not PARQUETS:
    pytest.skip(
        "Nenhum Parquet de BTCUSD encontrado — rode prepare_data.py primeiro",
        allow_module_level=True,
    )

# Funções + tipo de retorno esperado
PATTERNS = [
    ('detect_bos', bool),
    ('detect_choch', bool),
    ('detect_fvg', list),
    ('detect_order_blocks', list),
    ('detect_liquidity_zones', dict),
]

def random_slice(df, minutes=720, seed=42):
    rnd = random.Random(seed)
    if len(df) <= minutes:
        return df.copy()
    start = rnd.randint(0, len(df)-minutes)
    return df.iloc[start:start+minutes].reset_index(drop=True)

@pytest.fixture(scope='module', params=PARQUETS)
def sample_df(request):
    df = pd.read_parquet(request.param)
    seed = abs(hash(str(request.param))) % (2**32)
    return random_slice(df, minutes=720, seed=seed)

@pytest.mark.parametrize('func_name,expected', PATTERNS)
def test_pattern_real(sample_df, func_name, expected):
    func = getattr(patterns, func_name)
    result = func(sample_df)
    assert isinstance(result, expected)
