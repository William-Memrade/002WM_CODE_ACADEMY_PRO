---
source_file: "Trading/001WM_STRATEGY_BOT/tests/test_execution.py"
type: "code"
community: "Community 17"
location: "L241"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_17
---

# FakeMT5

## Connections
- [[dot-__init__()_42]] - `method` [EXTRACTED]
- [[dot-_make_mt5_with_order()]] - `calls` [EXTRACTED]
- [[dot-_run_auto()]] - `calls` [EXTRACTED]
- [[dot-account_info()]] - `method` [EXTRACTED]
- [[dot-order_send()_2]] - `method` [EXTRACTED]
- [[dot-orders_get()_2]] - `method` [EXTRACTED]
- [[dot-positions_get()]] - `method` [EXTRACTED]
- [[dot-setUp()_7]] - `calls` [EXTRACTED]
- [[dot-setUp()_10]] - `calls` [EXTRACTED]
- [[dot-symbol_info()_1]] - `method` [EXTRACTED]
- [[dot-symbol_info_tick()_1]] - `method` [EXTRACTED]
- [[dot-test_all_invalid_fillings_fail_with_invalid_filling_type()]] - `calls` [EXTRACTED]
- [[dot-test_auto_signal_with_blocked_news_waits_and_does_not_send_order()]] - `calls` [EXTRACTED]
- [[dot-test_auto_signal_with_news_ok_continues_normal_flow()]] - `calls` [EXTRACTED]
- [[dot-test_auto_trading_off_does_not_execute()]] - `calls` [EXTRACTED]
- [[dot-test_auto_trading_on_without_risk_confirmation_does_not_call_executor()]] - `calls` [EXTRACTED]
- [[dot-test_blocked_alert_does_not_show_mt5_order()]] - `calls` [EXTRACTED]
- [[dot-test_blocked_executable_levels_are_not_used_as_active_levels()]] - `calls` [EXTRACTED]
- [[dot-test_bot_owned_sell_limit_cancelled_on_news_block()]] - `calls` [EXTRACTED]
- [[dot-test_buy_above_entry_uses_buy_limit()]] - `calls` [EXTRACTED]
- [[dot-test_buy_below_entry_blocks()]] - `calls` [EXTRACTED]
- [[dot-test_buy_near_entry_uses_market_order()]] - `calls` [EXTRACTED]
- [[dot-test_calculated_volume_below_min_and_min_exceeds_risk_blocks()]] - `calls` [EXTRACTED]
- [[dot-test_calculated_volume_below_min_and_min_within_risk_uses_minimum()]] - `calls` [EXTRACTED]
- [[dot-test_cancel_failure_does_not_break_cycle()]] - `calls` [EXTRACTED]
- [[dot-test_disable_sl_distance_guard_still_blocks_max_allowed_risk()]] - `calls` [EXTRACTED]
- [[dot-test_execution_journal_saves_executed_attempt()]] - `calls` [EXTRACTED]
- [[dot-test_invalid_ioc_and_fok_retries_with_return()]] - `calls` [EXTRACTED]
- [[dot-test_invalid_ioc_retries_with_fok()]] - `calls` [EXTRACTED]
- [[dot-test_manual_order_without_magic_or_comment_not_cancelled()]] - `calls` [EXTRACTED]
- [[dot-test_market_alert_uses_execution_levels()]] - `calls` [EXTRACTED]
- [[dot-test_min_volume_risk_override_true_in_demo_allows_override()]] - `calls` [EXTRACTED]
- [[dot-test_min_volume_risk_override_true_in_real_allows_with_real_override()]] - `calls` [EXTRACTED]
- [[dot-test_min_volume_risk_override_true_in_real_blocks_without_real_override()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_execution_calls_pending_cancel_then_saves_wait()]] - `calls` [EXTRACTED]
- [[dot-test_news_blocked_no_new_market_or_pending_order()]] - `calls` [EXTRACTED]
- [[dot-test_no_pending_orders_returns_empty_and_no_crash()]] - `calls` [EXTRACTED]
- [[dot-test_order_send_called_when_disable_sl_distance_guard_allows_large_execution_sl()]] - `calls` [EXTRACTED]
- [[dot-test_order_send_not_called_when_selected_volume_exceeds_risk()]] - `calls` [EXTRACTED]
- [[dot-test_order_send_not_called_when_sl_distance_too_large()]] - `calls` [EXTRACTED]
- [[dot-test_original_h1_levels_are_ignored_and_trade_request_uses_execution_levels()]] - `calls` [EXTRACTED]
- [[dot-test_pending_alert_uses_pending_levels()]] - `calls` [EXTRACTED]
- [[dot-test_pending_invalid_expiration_retries_as_gtc_and_succeeds()]] - `calls` [EXTRACTED]
- [[dot-test_pending_invalid_expiration_retry_failure_returns_failed()]] - `calls` [EXTRACTED]
- [[dot-test_pending_recalculates_sl_tp_using_signal_entry()]] - `calls` [EXTRACTED]
- [[dot-test_pending_setup_store_updated_when_ticket_matches()]] - `calls` [EXTRACTED]
- [[dot-test_position_sizing_calculates_valid_volume()]] - `calls` [EXTRACTED]
- [[dot-test_selected_volume_exceeds_max_risk_blocks_execution()]] - `calls` [EXTRACTED]
- [[dot-test_sell_above_entry_blocks()]] - `calls` [EXTRACTED]
- [[dot-test_sell_below_entry_uses_sell_limit()]] - `calls` [EXTRACTED]
- [[dot-test_sell_near_entry_uses_market_order()]] - `calls` [EXTRACTED]
- [[dot-test_trade_executor_uses_mocked_order_send()]] - `calls` [EXTRACTED]
- [[dot-test_valid_signal_calls_trade_executor_with_mock()]] - `calls` [EXTRACTED]
- [[dot-test_waiting_alert_shows_no_mt5_order_sent()]] - `calls` [EXTRACTED]
- [[dot-test_waiting_for_retest_saved_when_pending_orders_disabled()]] - `calls` [EXTRACTED]
- [[TestAutoExecutionStatusGate]] - `uses` [INFERRED]
- [[test_execution.py]] - `contains` [EXTRACTED]
- [[test_signal_status.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_17