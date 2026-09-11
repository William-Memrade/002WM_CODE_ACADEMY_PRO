---
source_file: "Trading/001WM_STRATEGY_BOT/tests/test_execution.py"
type: "code"
community: "Community 10"
location: "L1195"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_10
---

# TestMainAutoExecution

## Connections
- [[dot-setUp()_9]] - `method` [EXTRACTED]
- [[dot-tearDown()]] - `method` [EXTRACTED]
- [[dot-test_auto_signal_with_blocked_news_waits_and_does_not_send_order()]] - `method` [EXTRACTED]
- [[dot-test_auto_signal_with_news_ok_continues_normal_flow()]] - `method` [EXTRACTED]
- [[dot-test_auto_trading_off_alert_can_show_technical_levels()]] - `method` [EXTRACTED]
- [[dot-test_auto_trading_on_without_risk_confirmation_does_not_call_executor()]] - `method` [EXTRACTED]
- [[dot-test_blocked_alert_does_not_show_mt5_order()]] - `method` [EXTRACTED]
- [[dot-test_blocked_executable_levels_are_not_used_as_active_levels()]] - `method` [EXTRACTED]
- [[dot-test_buy_above_entry_uses_buy_limit()]] - `method` [EXTRACTED]
- [[dot-test_buy_below_entry_blocks()]] - `method` [EXTRACTED]
- [[dot-test_buy_entry_decision_uses_executable_entry()]] - `method` [EXTRACTED]
- [[dot-test_buy_near_entry_uses_market_order()]] - `method` [EXTRACTED]
- [[dot-test_entry_decision_falls_back_to_original_signal_entry()]] - `method` [EXTRACTED]
- [[dot-test_eurusd_entry_decision_uses_executable_entry_precision()]] - `method` [EXTRACTED]
- [[dot-test_market_alert_uses_execution_levels()]] - `method` [EXTRACTED]
- [[dot-test_no_signal_not_persisted_when_disabled()]] - `method` [EXTRACTED]
- [[dot-test_order_send_called_when_disable_sl_distance_guard_allows_large_execution_sl()]] - `method` [EXTRACTED]
- [[dot-test_order_send_not_called_when_selected_volume_exceeds_risk()]] - `method` [EXTRACTED]
- [[dot-test_order_send_not_called_when_sl_distance_too_large()]] - `method` [EXTRACTED]
- [[dot-test_original_h1_levels_are_ignored_and_trade_request_uses_execution_levels()]] - `method` [EXTRACTED]
- [[dot-test_pending_alert_uses_pending_levels()]] - `method` [EXTRACTED]
- [[dot-test_pending_recalculates_sl_tp_using_signal_entry()]] - `method` [EXTRACTED]
- [[dot-test_price_too_far_from_executable_entry_uses_non_market_path()]] - `method` [EXTRACTED]
- [[dot-test_sell_above_entry_blocks()]] - `method` [EXTRACTED]
- [[dot-test_sell_below_entry_uses_sell_limit()]] - `method` [EXTRACTED]
- [[dot-test_sell_entry_decision_uses_executable_entry()]] - `method` [EXTRACTED]
- [[dot-test_sell_near_entry_uses_market_order()]] - `method` [EXTRACTED]
- [[dot-test_signal_store_duplicate_does_not_block_execution_evaluation()]] - `method` [EXTRACTED]
- [[dot-test_valid_signal_calls_trade_executor_with_mock()]] - `method` [EXTRACTED]
- [[dot-test_waiting_alert_shows_no_mt5_order_sent()]] - `method` [EXTRACTED]
- [[dot-test_waiting_for_news_after_block_end_rejects_direction_change()]] - `method` [EXTRACTED]
- [[dot-test_waiting_for_news_after_block_end_rejects_low_score()]] - `method` [EXTRACTED]
- [[dot-test_waiting_for_news_before_block_end_does_not_revalidate()]] - `method` [EXTRACTED]
- [[dot-test_waiting_for_retest_saved_when_pending_orders_disabled()]] - `method` [EXTRACTED]
- [[dot-test_watchlist_persisted_but_not_written_to_execution_journal()]] - `method` [EXTRACTED]
- [[ExecutionJournal]] - `uses` [INFERRED]
- [[ExecutionStatus]] - `uses` [INFERRED]
- [[PendingSetupStore]] - `uses` [INFERRED]
- [[RiskManager]] - `uses` [INFERRED]
- [[SignalFormatter]] - `uses` [INFERRED]
- [[test_execution.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_10