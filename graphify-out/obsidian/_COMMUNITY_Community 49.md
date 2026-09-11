---
type: community
cohesion: 0.08
members: 40
---

# Community 49

**Cohesion:** 0.08 - loosely connected
**Members:** 40 nodes

## Members
- [[dot-setUp()_17]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-setUp()_18]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_breakeven_exit_after_tp1()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_expired_max_bars()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_no_bars_after_signal()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_same_bar_ambiguity_conservative()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_same_bar_ambiguity_marked()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_same_bar_ambiguity_optimistic()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_sl_below_does_not_trigger()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_sl_hit()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_tp1_hit()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_buy_tp2_hit_with_partial()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_no_partial_tp_exits_at_tp1()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_slippage_worsens_effective_entry_buy()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_spread_contributes_to_total_cost()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[dot-test_spread_override_overrides_signal_spread()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[After TP1, if price drops to breakeven (entry), TP1_HIT with partial R.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Creates a SignalReplayEngine with explicit parameters (0 slippage by default…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Creates a synthetic OHLCV DataFrame with `n` uniform bars. All bars have the…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[DataFrame_22]] - code
- [[If no bars exist after signal timestamp, outcome is EXPIRED.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Low above SL should NOT trigger invalidation.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Position expires after max_bars_to_expire bars with no resolution.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Price hits SL before TP1 → INVALIDATED with -1.0 R.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Price reaches TP1 before SL → TP1_HIT outcome.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Price reaches TP1 then TP2 → TP2_HIT with partial R calculation.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Returns a standard BUY BacktestSignalRecord for testing.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Slippage increases effective entry for buys → less R to TP.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[TestReplayEngineBuy]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[TestReplayEnginePhase2]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[TestReplayEngineSlippage]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[Total cost = slippage + half_spread.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[When SL and TP1 both in same bar's range, conservative → INVALIDATED.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[When SL and TP1 both in same bar's range, optimistic → TP1_HIT.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[When ambiguity_resolution='ambiguous', outcome is AMBIGUOUS.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[With use_partial_tp=False, first TP1 hit is a full exit.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[make_buy_signal()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[make_candles()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[make_engine()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py
- [[spread_override_points replaces the signal's spread_points.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_backtesting.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_49
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Community 50]]
- 7 edges to [[_COMMUNITY_Community 175]]
- 4 edges to [[_COMMUNITY_Community 223]]
- 3 edges to [[_COMMUNITY_Community 62]]
- 3 edges to [[_COMMUNITY_Community 249]]
- 1 edge to [[_COMMUNITY_Community 52]]

## Top bridge nodes
- [[make_buy_signal()]] - degree 16, connects to 4 communities
- [[make_candles()]] - degree 21, connects to 3 communities
- [[make_engine()]] - degree 15, connects to 3 communities
- [[TestReplayEngineBuy]] - degree 12, connects to 2 communities
- [[TestReplayEnginePhase2]] - degree 5, connects to 2 communities