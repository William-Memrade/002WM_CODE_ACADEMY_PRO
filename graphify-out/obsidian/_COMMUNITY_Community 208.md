---
type: community
cohesion: 0.20
members: 11
---

# Community 208

**Cohesion:** 0.20 - loosely connected
**Members:** 11 nodes

## Members
- [[dot-_calculate_levels()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_detect_doji()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_detect_engulfing()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_detect_pin_bar()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_score_candle_patterns()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Calculates suggested entry, stop loss (invalidation), and take profit levels.…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Checks if a candle is a Doji. Doji Body is = 10% of the total candle range.]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Checks if a candle is a Pin Bar. Pin Bar Shadow = 2x body size AND body is =…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Checks if the last completed candle engulfs the previous one. Must be of…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Checks if the latest closed candles on H1 or M15 exhibit high-probability…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[DataFrame_7]] - code

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_208
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Community 15]]
- 2 edges to [[_COMMUNITY_Community 42]]

## Top bridge nodes
- [[dot-_score_candle_patterns()]] - degree 8, connects to 2 communities
- [[dot-_calculate_levels()]] - degree 5, connects to 2 communities
- [[dot-_detect_engulfing()]] - degree 4, connects to 1 community
- [[dot-_detect_doji()]] - degree 3, connects to 1 community
- [[dot-_detect_pin_bar()]] - degree 3, connects to 1 community