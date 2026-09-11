---
type: community
cohesion: 0.05
members: 86
---

# Community 15

**Cohesion:** 0.05 - loosely connected
**Members:** 86 nodes

## Members
- [[dot-_classify_strength()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_execution_timeframes_aligned()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_get_available_timeframes()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_log_buy_sell_audit()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_resolve_base_atr()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_score_divergence()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_score_fibonacci_confluence()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_score_microstructure()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_score_news_impact()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_score_setup()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_score_spread()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-_score_zone_proximity()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-evaluate()]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[dot-setUp()_4]] - code - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[dot-test_graceful_degradation()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[dot-test_mt5_epoch_seconds_are_converted_to_utc_aware_datetimes()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_critical_pipeline.py
- [[dot-test_news_blocked_high_score_produces_valid_signal()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[dot-test_news_blocked_low_score_no_waiting()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[dot-test_news_blocked_never_calls_order_send()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[dot-test_news_hard_block()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[dot-test_signal_input_default_timestamp_is_utc_aware()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_critical_pipeline.py
- [[dot-test_strong_aligned_signal()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[Calculates the score, reasons, warnings, and counter-trend flag for a specific…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Checks if a Fibonacci zone overlaps with the nearest supportresistance zone.]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Checks if a confirmed, strong divergence matches the signal direction.]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Checks if current price is inside or close (within 0.5 ATR) to a strong zone…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Combines technical confluences, multi-timeframe trend context, news filters,…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Constructs a list of timeframes for which datacontext is available.]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[DataFrame_1]] - code
- [[DivergenceResult]] - code - Trading/001WM_STRATEGY_BOT/app/indicators/divergence.py
- [[Evaluates the input confluences and returns a SignalCandidate. Args…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Grants points if lower timeframes M5 or M15 show a structure shift aligned with…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Grants points if the current bidask spread is within normal boundaries.]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Grants points if there is no high impact news, or penalizes if risk is…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Helper DataFrame with bullish engulfing pattern.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[Helper confirmed bullish divergence.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[Helper create a blocked news result.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[Helper create a fully aligned bullish context for high scores.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[Helper fib zone overlapping with support near 1850.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[Helper strong support zone near 1850.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[Maps a numeric score to one of four strength labels.]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[MarketRegime]] - code - Trading/001WM_STRATEGY_BOT/app/strategy/market_regime.py
- [[Minimal settings mock for classify_signal.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[NewsFilterResult]] - code - Trading/001WM_STRATEGY_BOT/app/news/models.py
- [[Resolves base ATR from context or raw DataFrames. Fallbacks to default.]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Result of evaluating market risk against recentupcoming news events. This…]] - rationale - Trading/001WM_STRATEGY_BOT/app/news/models.py
- [[Scenario 1 Maximum confluences aligned. Should score highly (12.0) and produce…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[Scenario 3 NewsFilterResult has allow_signal == False. Technical scoring…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[Scenario 5 Missing optional data inputs. Should evaluate cleanly without crash…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[ScoringEngine]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Signal scoring engine for the XAU Signal Bot. This module aggregates multi-…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[SignalInput]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Standardized input package passed to the ScoringEngine. Only `symbol`,…]] - rationale - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[Test 1 news blocked + technical score = 8.010 → waiting_for_news_clear. The…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[Test 2 news blocked + technical score ~5.010 → no_signal or watchlist, no…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[Test 3 news blocked with high score never calls mt5.order_send. Even when a…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[TestCriticalUtcHandling]] - code - Trading/001WM_STRATEGY_BOT/tests/test_critical_pipeline.py
- [[TestNewsBlockedHighScore]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[TestNewsBlockedLowScore]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[TestNewsBlockedNeverCallsOrderSend]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[TestScoringEngine]] - code - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[Tests for the news-blocked scoring flow. Validates that 1. News blocked + high…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[The result of a divergence scan on a single DataFrame  timeframe. Attributes…]] - rationale - Trading/001WM_STRATEGY_BOT/app/indicators/divergence.py
- [[Unit tests for the Signal Scoring Engine.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[_MockConfig]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[_context()_1]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[_divergence()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[_is_news_blocked()]] - code - Trading/001WM_STRATEGY_BOT/app/main.py
- [[_make_aligned_context()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[_make_divergence()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[_make_engulfing_df()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[_make_fib_zone()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[_make_news_blocked()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[_make_support_zone()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[_mock_regime()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[_zones()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[scoring.py]] - code - Trading/001WM_STRATEGY_BOT/app/signals/scoring.py
- [[signals__init__.py]] - code - Trading/001WM_STRATEGY_BOT/app/signals/__init__.py
- [[test_buy_can_pass_against_bearish_primary_context_when_intraday_score_is_high()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[test_buy_score_is_calculated_when_primary_context_is_bearish()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[test_buy_sell_balance.py]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[test_news_scoring_flow.py]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_scoring_flow.py
- [[test_scoring.py]] - code - Trading/001WM_STRATEGY_BOT/tests/test_scoring.py
- [[test_sell_can_pass_against_bullish_primary_context_when_counter_score_is_high()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[test_sell_can_pass_with_bearish_primary_and_bearish_intraday_alignment()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py
- [[test_sell_score_is_calculated_when_primary_context_is_bullish()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_buy_sell_balance.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_15
SORT file.name ASC
```

## Connections to other communities
- 23 edges to [[_COMMUNITY_Community 102]]
- 22 edges to [[_COMMUNITY_Community 60]]
- 19 edges to [[_COMMUNITY_Community 42]]
- 12 edges to [[_COMMUNITY_Community 5]]
- 12 edges to [[_COMMUNITY_Community 94]]
- 11 edges to [[_COMMUNITY_Community 10]]
- 11 edges to [[_COMMUNITY_Community 16]]
- 10 edges to [[_COMMUNITY_Community 62]]
- 9 edges to [[_COMMUNITY_Community 99]]
- 8 edges to [[_COMMUNITY_Community 18]]
- 8 edges to [[_COMMUNITY_Community 79]]
- 7 edges to [[_COMMUNITY_Community 208]]
- 6 edges to [[_COMMUNITY_Community 29]]
- 6 edges to [[_COMMUNITY_Community 110]]
- 6 edges to [[_COMMUNITY_Community 195]]
- 5 edges to [[_COMMUNITY_Community 47]]
- 5 edges to [[_COMMUNITY_Community 222]]
- 5 edges to [[_COMMUNITY_Community 64]]
- 4 edges to [[_COMMUNITY_Community 32]]
- 4 edges to [[_COMMUNITY_Community 39]]
- 3 edges to [[_COMMUNITY_Community 129]]
- 3 edges to [[_COMMUNITY_Community 63]]
- 3 edges to [[_COMMUNITY_Community 162]]
- 3 edges to [[_COMMUNITY_Community 45]]
- 2 edges to [[_COMMUNITY_Community 154]]
- 1 edge to [[_COMMUNITY_Community 345]]
- 1 edge to [[_COMMUNITY_Community 153]]
- 1 edge to [[_COMMUNITY_Community 137]]
- 1 edge to [[_COMMUNITY_Community 152]]
- 1 edge to [[_COMMUNITY_Community 168]]
- 1 edge to [[_COMMUNITY_Community 28]]

## Top bridge nodes
- [[scoring.py]] - degree 54, connects to 24 communities
- [[ScoringEngine]] - degree 62, connects to 12 communities
- [[test_news_scoring_flow.py]] - degree 35, connects to 11 communities
- [[SignalInput]] - degree 49, connects to 9 communities
- [[NewsFilterResult]] - degree 25, connects to 8 communities