from data.fetchers.yf_fetcher import fetch_yf


def test_fetch_btc_daily():
    df = fetch_yf("BTC-USD", "1d", "2024-01-01", "2024-01-03")
    assert not df.empty
    assert {"open", "high", "low", "close"}.issubset(df.columns.str.lower())
