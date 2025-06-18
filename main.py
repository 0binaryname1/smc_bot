#!/usr/bin/env python3
import os
import sys

# ────────────────────────────────────────────────────────────────────────────────
# 1) Insere a raiz do projeto no topo de sys.path
#    Isso faz com que "import backtest.engine" e "import core.patterns" funcionem
#
#    dirname(__file__) = pasta onde main.py vive (C:/Users/Esdras/smc_bot)
# ────────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ────────────────────────────────────────────────────────────────────────────────

import argparse
from backtest.engine import run_backtests
from config import ASSETS, TIMEFRAME, START_DATE

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeframe", default=TIMEFRAME)
    parser.add_argument("--start",     default=START_DATE)
    args = parser.parse_args()

    df = run_backtests(ASSETS, args.timeframe, args.start)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
