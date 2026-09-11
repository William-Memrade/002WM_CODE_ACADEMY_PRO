---
source_file: "Trading/001WM_STRATEGY_BOT/app/strategy/market_context.py"
type: "code"
community: "Community 60"
location: "L494"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_60
---

# _resolve_allowed_direction()

## Connections
- [[AllowedDirection]] - `references` [EXTRACTED]
- [[Determines which trade directions the context permits. Rules - H4 bullish AND…]] - `rationale_for` [EXTRACTED]
- [[TimeframeTrend]] - `references` [EXTRACTED]
- [[TrendLabel]] - `references` [EXTRACTED]
- [[_execution_timeframes_align()]] - `calls` [EXTRACTED]
- [[classify_market_context()]] - `calls` [EXTRACTED]
- [[market_context.py]] - `contains` [EXTRACTED]
- [[test_buy_allowed_when_execution_timeframes_align_even_if_h1_m30_bearish()]] - `calls` [EXTRACTED]
- [[test_buy_sell_balance.py]] - `imports` [EXTRACTED]
- [[test_h1_m30_bearish_ranging_execution_does_not_force_sell_only()]] - `calls` [EXTRACTED]
- [[test_h1_m30_bullish_bearish_execution_does_not_force_buy_only()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_60