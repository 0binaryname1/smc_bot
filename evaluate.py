from data.fetchers.yf_fetcher import fetch_yf
import pandas as pd
from datetime import datetime, timedelta

# 1. Tickers corrigidos
ativos = {
    "Mini-Índice": "^BVSP",
    "EUR/USD":     "EURUSD=X",
    "BTC/USD":     "BTC-USD",
}

pesos = {
    "liquidez":     0.35,
    "volatilidade": 0.30,
    # custas, janelas, dados, reg, divers. somam 0.35 mas vamos focar agora só nestes dois
}

start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
metrics = []

for nome, ticker in ativos.items():
    try:
        df = fetch_yf(ticker, "1d", start)
    except Exception as e:
        print(f"⚠️  Erro ao baixar {nome} ({ticker}): {e}")
        continue

    # Calcular range e ATR%
    df["range"] = df["high"] - df["low"]
    avg_atr_pct = (df["range"].mean() / df["close"].mean()) * 100

    # Se não há coluna volume (Forex), usamos o range médio como proxy de liquidez
    if "volume" in df.columns and df["volume"].notna().any():
        avg_vol = df["volume"].mean()
    else:
        avg_vol = df["range"].mean()  # substituto para liquidez

    metrics.append({
        "ativo":       nome,
        "avg_vol":     avg_vol,
        "avg_atr_pct": avg_atr_pct,
    })

dfm = pd.DataFrame(metrics)

# Normalização [0,1]
for col in ["avg_vol", "avg_atr_pct"]:
    mn, mx = dfm[col].min(), dfm[col].max()
    dfm[f"norm_{col}"] = (dfm[col] - mn) / (mx - mn) if mx > mn else 1.0

# Score ponderado
dfm["score"] = (
    pesos["liquidez"]     * dfm["norm_avg_vol"] +
    pesos["volatilidade"] * dfm["norm_avg_atr_pct"]
)

# Mostrar ranking
print(dfm[["ativo","avg_vol","avg_atr_pct","score"]].sort_values("score", ascending=False))
