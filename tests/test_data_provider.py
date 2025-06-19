import os
import pickle
import pandas as pd
import pytest
from pathlib import Path

import data.data_provider as dp

class DummyDF(pd.DataFrame):
    """Usado só pra identificar instância."""
    pass

@pytest.fixture(autouse=True)
def make_cache_dir(tmp_path, monkeypatch):
    # força usar pasta temporária para cache
    monkeypatch.setattr(dp, "CACHE_DIR", tmp_path / "cache")
    return tmp_path

def test_yf_provider(tmp_path, monkeypatch):
    # cria DataFrame dummy para Yahoo
    df_dummy = DummyDF({"open":[1], "high":[2], "low":[0], "close":[1.5]})
    called = {}
    def fake_fetch_yf(symbol, tf, start, end):
        called['yf'] = True
        return df_dummy
    monkeypatch.setattr(dp, "fetch_yf", fake_fetch_yf)

    out = dp.get_data("SYM", "1d", "2020-01-01", "2020-01-02", provider="yf")
    assert isinstance(out, pd.DataFrame)
    pd.testing.assert_frame_equal(out, df_dummy)
    assert called.get('yf') is True

    # deve ter criado arquivo de cache
    cache_files = list((dp.CACHE_DIR).glob("SYM-1d_2020-01-01_2020-01-02_yf.pkl"))
    assert cache_files, "Cache não foi gravado"

    # segunda chamada não aciona mais fetch
    called.clear()
    out2 = dp.get_data("SYM", "1d", "2020-01-01", "2020-01-02", provider="yf")
    assert called == {}, "Não deveria chamar fetch de novo"
    assert out2.equals(df_dummy)

def test_av_provider(tmp_path, monkeypatch):
    # cria DataFrame dummy para AV
    df_dummy = DummyDF({"open":[10], "high":[20], "low":[5], "close":[15]})
    called = {}
    def fake_fetch_av(symbol, tf, start, end, api_key):
        called['av'] = api_key
        return df_dummy
    monkeypatch.setattr(dp, "fetch_av", fake_fetch_av)

    # sem api_key deve erro
    with pytest.raises(ValueError):
        dp.get_data("SYM", "1d", "2020-01-01", "2020-01-02", provider="av")

    # com api_key
    out = dp.get_data("SYM", "1d", "2020-01-01", "2020-01-02", provider="av", api_key="KEY123")
    assert out is df_dummy
    assert called.get('av') == "KEY123"

    # cache foi gerado
    assert (dp.CACHE_DIR / "SYM-1d_2020-01-01_2020-01-02_av.pkl").exists()

def test_invalid_provider(tmp_path):
    with pytest.raises(ValueError):
        dp.get_data("SYM", "1d", "2020-01-01", "2020-01-02", provider="xxx")
