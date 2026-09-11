---
source_file: "Trading/001WM_STRATEGY_BOT/tests/test_telegram_notifications.py"
type: "code"
community: "Community 28"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_28
---

# test_telegram_notifications.py

## Connections
- [[ActiveTradeManager]] - `imports` [EXTRACTED]
- [[FakeNotifier]] - `contains` [EXTRACTED]
- [[SignalCandidate]] - `imports` [EXTRACTED]
- [[SignalClassification]] - `imports` [EXTRACTED]
- [[SignalStatus]] - `imports` [EXTRACTED]
- [[TelegramNotifier]] - `imports` [EXTRACTED]
- [[TradeOutcomeTracker]] - `imports` [EXTRACTED]
- [[_config()_1]] - `contains` [EXTRACTED]
- [[_dispatch_alert()]] - `imports` [EXTRACTED]
- [[_send_execution_telegram()]] - `imports` [EXTRACTED]
- [[active_trade_manager.py]] - `imports_from` [EXTRACTED]
- [[clean_telegram_text()]] - `imports` [EXTRACTED]
- [[format_auto_trade_filled_log()]] - `imports` [EXTRACTED]
- [[format_auto_trade_filled_telegram()]] - `imports` [EXTRACTED]
- [[formatter.py]] - `imports_from` [EXTRACTED]
- [[scoring.py]] - `imports_from` [EXTRACTED]
- [[send_telegram_message()]] - `imports` [EXTRACTED]
- [[status.py]] - `imports_from` [EXTRACTED]
- [[telegram.py]] - `imports_from` [EXTRACTED]
- [[test_auto_trade_filled_sends_message()]] - `contains` [EXTRACTED]
- [[test_auto_trade_filled_telegram_is_compact_and_log_keeps_mt5_ids()]] - `contains` [EXTRACTED]
- [[test_blocked_open_position_limit_not_sent_to_telegram()]] - `contains` [EXTRACTED]
- [[test_clean_telegram_text_removes_control_chars()]] - `contains` [EXTRACTED]
- [[test_missing_token_or_chat_id_does_not_break_bot()]] - `contains` [EXTRACTED]
- [[test_partial_close_sends_message()]] - `contains` [EXTRACTED]
- [[test_pending_order_blocked_sends_message()]] - `contains` [EXTRACTED]
- [[test_pending_order_placed_not_sent_when_only_filled_and_important()]] - `contains` [EXTRACTED]
- [[test_pending_order_placed_sends_message()]] - `contains` [EXTRACTED]
- [[test_repeated_critical_blocked_is_deduped()]] - `contains` [EXTRACTED]
- [[test_signal_formatter_alert_does_not_send_telegram()]] - `contains` [EXTRACTED]
- [[test_sl_moved_to_breakeven_sends_message()]] - `contains` [EXTRACTED]
- [[test_technical_log_text_is_not_sent_by_router()]] - `contains` [EXTRACTED]
- [[test_telegram_disabled_sends_nothing()]] - `contains` [EXTRACTED]
- [[test_telegram_enabled_with_token_chat_sends_message()]] - `contains` [EXTRACTED]
- [[test_trade_closed_tp_sl_sends_message()]] - `contains` [EXTRACTED]
- [[trade_outcome_tracker.py]] - `imports_from` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_28