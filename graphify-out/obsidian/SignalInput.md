---
source_file: "Trading/001WM_STRATEGY_BOT/app/signals/scoring.py"
type: "code"
community: "Community 15"
location: "L43"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_15
---

# SignalInput

## Connections
- [[dot-_get_available_timeframes()]] - `references` [EXTRACTED]
- [[dot-_log_buy_sell_audit()]] - `references` [EXTRACTED]
- [[dot-_resolve_base_atr()]] - `references` [EXTRACTED]
- [[dot-_score_setup()]] - `references` [EXTRACTED]
- [[dot-evaluate()]] - `references` [EXTRACTED]
- [[dot-test_counter_trend_signal()]] - `calls` [EXTRACTED]
- [[dot-test_graceful_degradation()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_high_score_produces_valid_signal()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_low_score_no_waiting()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_never_calls_order_send()]] - `calls` [EXTRACTED]
- [[dot-test_news_hard_block()]] - `calls` [EXTRACTED]
- [[dot-test_signal_input_default_timestamp_is_utc_aware()]] - `calls` [EXTRACTED]
- [[dot-test_strong_aligned_signal()]] - `calls` [EXTRACTED]
- [[dot-test_trend_alignment_conflict()]] - `calls` [EXTRACTED]
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[DivergenceResult]] - `uses` [INFERRED]
- [[MarketContext]] - `uses` [INFERRED]
- [[NewsFilterResult]] - `uses` [INFERRED]
- [[PriceZone]] - `uses` [INFERRED]
- [[Standardized input package passed to the ScoringEngine. Only `symbol`,…]] - `rationale_for` [EXTRACTED]
- [[TestCriticalUtcHandling]] - `uses` [INFERRED]
- [[TestNewsBlockedHighScore]] - `uses` [INFERRED]
- [[TestNewsBlockedLowScore]] - `uses` [INFERRED]
- [[TestNewsBlockedNeverCallsOrderSend]] - `uses` [INFERRED]
- [[TestScoringEngine]] - `uses` [INFERRED]
- [[_analyse_symbol()]] - `calls` [EXTRACTED]
- [[_input()]] - `calls` [EXTRACTED]
- [[backtest_new_rules_report.py]] - `imports` [EXTRACTED]
- [[backtest_symbol()]] - `calls` [EXTRACTED]
- [[backtest_symbol()_1]] - `calls` [EXTRACTED]
- [[backtest_xau_adaptive.py]] - `imports` [EXTRACTED]
- [[fast_backtest_forex_rules.py]] - `imports` [EXTRACTED]
- [[montgomery_backtest.py]] - `imports` [EXTRACTED]
- [[montgomery_backtest_fast.py]] - `imports` [EXTRACTED]
- [[run_backtest()]] - `calls` [EXTRACTED]
- [[run_symbol()]] - `calls` [EXTRACTED]
- [[run_symbol()_1]] - `calls` [EXTRACTED]
- [[scoring.py]] - `contains` [EXTRACTED]
- [[signals__init__.py]] - `imports` [EXTRACTED]
- [[test_buy_can_pass_against_bearish_primary_context_when_intraday_score_is_high()]] - `calls` [EXTRACTED]
- [[test_buy_score_is_calculated_when_primary_context_is_bearish()]] - `calls` [EXTRACTED]
- [[test_buy_sell_balance.py]] - `imports` [EXTRACTED]
- [[test_critical_pipeline.py]] - `imports` [EXTRACTED]
- [[test_news_scoring_flow.py]] - `imports` [EXTRACTED]
- [[test_scoring.py]] - `imports` [EXTRACTED]
- [[test_sell_can_pass_against_bullish_primary_context_when_counter_score_is_high()]] - `calls` [EXTRACTED]
- [[test_sell_can_pass_with_bearish_primary_and_bearish_intraday_alignment()]] - `calls` [EXTRACTED]
- [[test_sell_score_is_calculated_when_primary_context_is_bullish()]] - `calls` [EXTRACTED]
- [[test_structure_first.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_15