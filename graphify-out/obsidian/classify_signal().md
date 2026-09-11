---
source_file: "Trading/001WM_STRATEGY_BOT/app/signals/status.py"
type: "code"
community: "Community 10"
location: "L59"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_10
---

# classify_signal()

## Connections
- [[dot-_run_auto()]] - `calls` [EXTRACTED]
- [[dot-format_message()]] - `calls` [EXTRACTED]
- [[dot-test_auto_signal_with_blocked_news_waits_and_does_not_send_order()]] - `calls` [EXTRACTED]
- [[dot-test_auto_signal_with_news_ok_continues_normal_flow()]] - `calls` [EXTRACTED]
- [[dot-test_auto_trading_off_alert_can_show_technical_levels()]] - `calls` [EXTRACTED]
- [[dot-test_auto_trading_off_does_not_execute()]] - `calls` [EXTRACTED]
- [[dot-test_auto_trading_on_without_risk_confirmation_does_not_call_executor()]] - `calls` [EXTRACTED]
- [[dot-test_blocked_alert_does_not_show_mt5_order()]] - `calls` [EXTRACTED]
- [[dot-test_buy_above_entry_uses_buy_limit()]] - `calls` [EXTRACTED]
- [[dot-test_buy_below_entry_blocks()]] - `calls` [EXTRACTED]
- [[dot-test_buy_near_entry_uses_market_order()]] - `calls` [EXTRACTED]
- [[dot-test_low_score_high_risk_sell_is_not_potential_signal()]] - `calls` [EXTRACTED]
- [[dot-test_market_alert_uses_execution_levels()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_execution_calls_pending_cancel_then_saves_wait()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_high_score_produces_valid_signal()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_low_score_no_waiting()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_never_calls_order_send()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_no_new_market_or_pending_order()]] - `calls` [EXTRACTED]
- [[dot-test_order_send_called_when_disable_sl_distance_guard_allows_large_execution_sl()]] - `calls` [EXTRACTED]
- [[dot-test_order_send_not_called_when_selected_volume_exceeds_risk()]] - `calls` [EXTRACTED]
- [[dot-test_order_send_not_called_when_sl_distance_too_large()]] - `calls` [EXTRACTED]
- [[dot-test_original_h1_levels_are_ignored_and_trade_request_uses_execution_levels()]] - `calls` [EXTRACTED]
- [[dot-test_pending_alert_uses_pending_levels()]] - `calls` [EXTRACTED]
- [[dot-test_pending_recalculates_sl_tp_using_signal_entry()]] - `calls` [EXTRACTED]
- [[dot-test_score_6_4_medium_risk_is_watchlist()]] - `calls` [EXTRACTED]
- [[dot-test_score_7_4_medium_risk_is_actionable()]] - `calls` [EXTRACTED]
- [[dot-test_score_8_high_risk_is_blocked_high_risk()]] - `calls` [EXTRACTED]
- [[dot-test_sell_above_entry_blocks()]] - `calls` [EXTRACTED]
- [[dot-test_sell_below_entry_uses_sell_limit()]] - `calls` [EXTRACTED]
- [[dot-test_sell_near_entry_uses_market_order()]] - `calls` [EXTRACTED]
- [[dot-test_valid_signal_calls_trade_executor_with_mock()]] - `calls` [EXTRACTED]
- [[dot-test_waiting_alert_shows_no_mt5_order_sent()]] - `calls` [EXTRACTED]
- [[dot-test_waiting_for_news_after_block_end_rejects_direction_change()]] - `calls` [EXTRACTED]
- [[dot-test_waiting_for_news_after_block_end_rejects_low_score()]] - `calls` [EXTRACTED]
- [[dot-test_waiting_for_news_before_block_end_does_not_revalidate()]] - `calls` [EXTRACTED]
- [[dot-test_waiting_for_retest_saved_when_pending_orders_disabled()]] - `calls` [EXTRACTED]
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[Any_13]] - `references` [EXTRACTED]
- [[Classify a candidate using normalized score and configured thresholds.]] - `rationale_for` [EXTRACTED]
- [[SignalCandidate]] - `uses` [INFERRED]
- [[SignalClassification]] - `calls` [EXTRACTED]
- [[_append_unique()]] - `calls` [EXTRACTED]
- [[_log_score_classification()]] - `calls` [EXTRACTED]
- [[classify_signal_status()]] - `calls` [EXTRACTED]
- [[formatter.py]] - `imports` [EXTRACTED]
- [[normalized_score()]] - `calls` [EXTRACTED]
- [[risk_level_from_candidate()]] - `calls` [EXTRACTED]
- [[run_cycle()]] - `calls` [EXTRACTED]
- [[status.py]] - `contains` [EXTRACTED]
- [[test_execution.py]] - `imports` [EXTRACTED]
- [[test_news_scoring_flow.py]] - `imports` [EXTRACTED]
- [[test_signal_status.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_10