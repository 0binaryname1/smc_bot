import os
import pickle
import pandas as pd
import pytest
from pathlib import Path

import data.data_provider as dp

@pytest.fixture(autouse=True)
def make_cache_dir(tmp_path, monkeypatch):
    # for├ºa usar pasta tempor├íria para cache
    monkeypatch.setattr(dp, "CACHE_DIR", tmp_path / "cache")
    return tmp_path

def test_yf_provider(tmp_path, monkeypatch):
    # cria DataFrame dummy para Yahoo
    df_dummy = pd.DataFrame({"open":[1], "high":[2], "low":[0], "close":[1.5]})
    called = {}
    def fake_fetch_yf(symbol, tf, start, end):
        called['yf'] = True
        return df_dummy
    monkeypatch.setattr(dp, "fetch_yf", fake_fetch_yf)

    out = dp.get_data("SYM", "1d", "2020-01-01", "2020-01-02", provider="yf")
    assert isinstance(out, pd.DataFrame)
    pd.testing.assert_frame_equal(out, df_dummy)

    # deve ter criado arquivo de cache
    cache_files = list((dp.CACHE_DIR).glob("SYM-1d_2020-01-01_2020-01-02_yf.pkl"))
    assert cache_files, "Cache n├úo foi gravado"

    # segunda chamada n├úo aciona mais fetch
    called.clear()
    out2 = dp.get_data("SYM", "1d", "2020-01-01", "2020-01-02", provider="yf")
    assert called == {}, "N├úo deveria chamar fetch de novo"
    pd.testing.assert_frame_equal(out2, df_dummy)

def test_av_provider(tmp_path, monkeypatch):
    # cria DataFrame dummy para AV
    df_dummy = pd.DataFrame({"open":[10], "high":[20], "low":[5], "close":[15]})
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
    pd.testing.assert_frame_equal(out, df_dummy)
    assert called.get('av') == "KEY123"

    # cache foi gerado
    assert (dp.CACHE_DIR / "SYM-1d_2020-01-01_2020-01-02_av.pkl").exists()

def test_invalid_provider(tmp_path):
    with pytest.raises(ValueError):
        dp.get_data("SYM", "1d", "2020-01-01", "2020-01-02", provider="xxx")
