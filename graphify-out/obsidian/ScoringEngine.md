---
source_file: "Trading/001WM_STRATEGY_BOT/app/signals/scoring.py"
type: "code"
community: "Community 15"
location: "L116"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_15
---

# ScoringEngine

## Connections
- [[dot-__init__()_36]] - `method` [EXTRACTED]
- [[dot-_apply_strategy_profile()]] - `method` [EXTRACTED]
- [[dot-_calculate_levels()]] - `method` [EXTRACTED]
- [[dot-_classify_strength()]] - `method` [EXTRACTED]
- [[dot-_detect_doji()]] - `method` [EXTRACTED]
- [[dot-_detect_engulfing()]] - `method` [EXTRACTED]
- [[dot-_detect_pin_bar()]] - `method` [EXTRACTED]
- [[dot-_execution_timeframes_aligned()]] - `method` [EXTRACTED]
- [[dot-_get_available_timeframes()]] - `method` [EXTRACTED]
- [[dot-_log_buy_sell_audit()]] - `method` [EXTRACTED]
- [[dot-_resolve_base_atr()]] - `method` [EXTRACTED]
- [[dot-_score_candle_patterns()]] - `method` [EXTRACTED]
- [[dot-_score_divergence()]] - `method` [EXTRACTED]
- [[dot-_score_fibonacci_confluence()]] - `method` [EXTRACTED]
- [[dot-_score_microstructure()]] - `method` [EXTRACTED]
- [[dot-_score_news_impact()]] - `method` [EXTRACTED]
- [[dot-_score_setup()]] - `method` [EXTRACTED]
- [[dot-_score_spread()]] - `method` [EXTRACTED]
- [[dot-_score_zone_proximity()]] - `method` [EXTRACTED]
- [[dot-evaluate()]] - `method` [EXTRACTED]
- [[dot-setUp()_4]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_high_score_produces_valid_signal()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_low_score_no_waiting()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_never_calls_order_send()]] - `calls` [EXTRACTED]
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[Combines technical confluences, multi-timeframe trend context, news filters,…]] - `rationale_for` [EXTRACTED]
- [[DivergenceResult]] - `uses` [INFERRED]
- [[MarketContext]] - `uses` [INFERRED]
- [[MarketRegime]] - `uses` [INFERRED]
- [[NewsFilterResult]] - `uses` [INFERRED]
- [[PriceZone]] - `uses` [INFERRED]
- [[SLTPOptimizer]] - `uses` [INFERRED]
- [[ScoringFeedback]] - `uses` [INFERRED]
- [[TestNewsBlockedHighScore]] - `uses` [INFERRED]
- [[TestNewsBlockedLowScore]] - `uses` [INFERRED]
- [[TestNewsBlockedNeverCallsOrderSend]] - `uses` [INFERRED]
- [[TestScoringEngine]] - `uses` [INFERRED]
- [[_analyse_symbol()]] - `uses` [INFERRED]
- [[backtest_new_rules_report.py]] - `imports` [EXTRACTED]
- [[backtest_symbol()]] - `calls` [EXTRACTED]
- [[backtest_symbol()_1]] - `calls` [EXTRACTED]
- [[backtest_xau_adaptive.py]] - `imports` [EXTRACTED]
- [[fast_backtest_forex_rules.py]] - `imports` [EXTRACTED]
- [[main()_13]] - `calls` [EXTRACTED]
- [[montgomery_backtest.py]] - `imports` [EXTRACTED]
- [[montgomery_backtest_fast.py]] - `imports` [EXTRACTED]
- [[run_backtest()]] - `calls` [EXTRACTED]
- [[run_cycle()]] - `uses` [INFERRED]
- [[run_symbol()]] - `calls` [EXTRACTED]
- [[run_symbol()_1]] - `calls` [EXTRACTED]
- [[scoring.py]] - `contains` [EXTRACTED]
- [[signals__init__.py]] - `imports` [EXTRACTED]
- [[test_buy_can_pass_against_bearish_primary_context_when_intraday_score_is_high()]] - `calls` [EXTRACTED]
- [[test_buy_score_is_calculated_when_primary_context_is_bearish()]] - `calls` [EXTRACTED]
- [[test_buy_sell_balance.py]] - `imports` [EXTRACTED]
- [[test_counter_context_requires_higher_score()]] - `calls` [EXTRACTED]
- [[test_news_scoring_flow.py]] - `imports` [EXTRACTED]
- [[test_scoring.py]] - `imports` [EXTRACTED]
- [[test_sell_can_pass_against_bullish_primary_context_when_counter_score_is_high()]] - `calls` [EXTRACTED]
- [[test_sell_can_pass_with_bearish_primary_and_bearish_intraday_alignment()]] - `calls` [EXTRACTED]
- [[test_sell_score_is_calculated_when_primary_context_is_bullish()]] - `calls` [EXTRACTED]
- [[test_structure_first.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_15