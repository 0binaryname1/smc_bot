#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Só processa o CSV de BTCUSD em chunks e gera Parquet.
"""
import pandas as pd
from pathlib import Path
import sys

DATA_DIR = Path(__file__).parent

def process_btc(csv_file: Path):
    usecols = ["Open time", "Open", "High", "Low", "Close", "Volume"]
    for i, chunk in enumerate(pd.read_csv(
        csv_file,
        usecols=usecols,
        parse_dates=["Open time"],
        chunksize=500_000,
    )):
        if chunk["Open time"].dtype == "int64":
            chunk["Open time"] = pd.to_datetime(
                chunk["Open time"], unit="ms", utc=True
            )
        chunk = chunk.rename(columns={
            "Open time": "datetime",
            "Open":       "open",
            "High":       "high",
            "Low":        "low",
            "Close":      "close",
            "Volume":     "volume",
        })
        out = csv_file.parent / f"btc_m1_part{i}.parquet"
        chunk.to_parquet(out, index=False, compression="snappy")
        print(f" → Gerado {out.name}")

def main():
    # só pega arquivos que contenham 'btcusd'
    csvs = [p for p in DATA_DIR.glob("*.csv") if "btcusd" in p.stem.lower()]
    if not csvs:
        print("⚠️  Não achei CSVs de BTCUSD em", DATA_DIR, file=sys.stderr)
        sys.exit(1)

    for csv in csvs:
        print(f"▶ Processando BTC   ({csv.name})")
        process_btc(csv)

    print("✅ Parquets de BTC gerados em", DATA_DIR)

if __name__ == "__main__":
    main()

