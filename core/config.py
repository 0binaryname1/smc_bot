# core/config.py

# Quantas ocorrências mínimas de highs/lows para formar zona de liquidez
LIQUIDITY_MIN_TOUCHES = 2

# Tolerância (em % ou valor absoluto) para considerar dois highs “iguais”
LIQUIDITY_TOLERANCE = 0.001  # ex.: 0.1%

# Proporção mínima de corpo do candle para validar um sweep
SWEEP_BODY_RATIO = 0.7

# Margem de “sweep parcial”: max de quanto ultrapassa a zona em % 
SWEEP_PARTIAL_MARGIN = 0.001

