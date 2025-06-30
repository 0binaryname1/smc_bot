# core/config.py

from datetime import datetime
from typing import List, Dict
# import dos detectores para montar os grupos
from core.patterns import (
    detect_bos,
    detect_choch,
    detect_fvg,
    detect_order_blocks,
    detect_liquidity_zones,
    detect_liquidity_sweep,
    detect_inducement,
    compute_equilibrium_zone,
    detect_killzones,
    detect_mss,
    detect_breaker_blocks,
    detect_confluence_zones,
    detect_mitigation_blocks,
    detect_liquidity_voids,
    detect_stop_hunts,
    detect_multi_fvg,
    detect_order_flow_imbalance,
)

# 1) ativos disponíveis (prefixos dos arquivos .parquet)
ASSETS: List[str] = ["BTCUSD", "XAUUSD", "EURUSD", "USDJPY"]

# 2) timeframes permitidos
TIMEFRAMES: List[str] = ["M1", "M5", "M15", "H1", "D1"]

# 3) data-padrão de início para backtest
START_DATE: datetime = datetime(2020, 1, 1)

# 4) detectores por nível
DETECTORS_BASIC = [
    detect_bos,
    detect_choch,
    detect_fvg,
    detect_order_blocks,
    detect_liquidity_zones,
    detect_liquidity_sweep,
]

DETECTORS_INTERMEDIATE = [
    detect_inducement,
    compute_equilibrium_zone,
    detect_killzones,
]

DETECTORS_ADVANCED = [
    detect_mss,
    detect_breaker_blocks,
    detect_confluence_zones,
    detect_mitigation_blocks,
    detect_liquidity_voids,
    detect_stop_hunts,
    detect_multi_fvg,
    detect_order_flow_imbalance,
]

DETECTORS_BY_LEVEL: Dict[str, List] = {
    "Básico": DETECTORS_BASIC,
    "Intermediário": DETECTORS_INTERMEDIATE,
    "Avançado": DETECTORS_ADVANCED,
}

