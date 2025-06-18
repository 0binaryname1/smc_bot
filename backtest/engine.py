from core.data_provider import get_provider
from core.patterns import detect_bos, detect_choch
import argparse


def run_backtests(
    tickers,
    timeframe: str,
    start: str,
    end: str,
    provider_name: str = "yf",
    api_key: str = None,
):
    # mapeia alias para provedor real
    key = provider_name.lower()
    if key in ("yf", "yahoo"):
        provider_key = "yahoo"
    elif key in ("av", "alpha", "alphavantage", "alpha_vantage"):
        provider_key = "alpha_vantage"
    else:
        raise ValueError(f"Provedor desconhecido: {provider_name}")

    provider = get_provider(provider_key, api_key=api_key)
    results = []
    for symbol in tickers:
        # busca os dados
        df = provider.fetch(symbol, timeframe, start, end)

        # aplica padrões (exemplos provisórios)
        df["is_bos"] = df.apply(lambda row: detect_bos(df, row.name), axis=1)
        df["is_choch"] = df.apply(lambda row: detect_choch(df, row.name), axis=1)

        # aqui você pode calcular métricas, trades, etc.
        results.append((symbol, df))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", default=None)
    parser.add_argument(
        "--provider",
        choices=["yf", "av"],
        default="yf",
        help="Escolha do provedor de dados: yf (Yahoo Finance) ou av (Alpha Vantage)",
    )
    parser.add_argument("--api-key", default=None)
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["BTC-USD", "EURUSD=X"],
        help="Lista de símbolos para backtest",
    )
    args = parser.parse_args()

    backtests = run_backtests(
        tickers=args.symbols,
        timeframe=args.timeframe,
        start=args.start,
        end=args.end,
        provider_name=args.provider,
        api_key=args.api_key,
    )

    for symbol, df in backtests:
        print(f"Resultados para {symbol}: {len(df)} candles carregados")
