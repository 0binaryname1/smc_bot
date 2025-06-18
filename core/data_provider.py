from typing import Protocol
import pandas as pd


class DataProvider(Protocol):
    def fetch(self, ticker: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        ...


class YahooProvider:
    """
    Provedor de dados usando Yahoo Finance
    """
    def fetch(self, ticker: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        from data.fetchers.yf_fetcher import fetch_yf
        return fetch_yf(ticker, timeframe, start, end)


class AlphaProvider:
    """
    Provedor de dados usando Alpha Vantage
    """
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch(self, ticker: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        from data.fetchers.av_fetcher import fetch_av
        return fetch_av(ticker, timeframe, start, end, api_key=self.api_key)


def get_provider(name: str, **kwargs) -> DataProvider:
    """
    Fábrica que retorna o provedor correto:
      - 'yahoo' -> YahooProvider
      - 'alpha' / 'av' -> AlphaProvider
    """
    name = name.lower()
    if name == "yahoo":
        return YahooProvider()
    elif name in ("alpha", "alpha_vantage", "av"):
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("API key is required for Alpha Vantage")
        return AlphaProvider(api_key=api_key)
    else:
        raise ValueError(f"Unknown data provider: {name}")
