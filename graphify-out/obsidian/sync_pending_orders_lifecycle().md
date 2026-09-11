---
source_file: "Trading/001WM_STRATEGY_BOT/app/execution/pending_order_manager.py"
type: "code"
community: "Community 101"
location: "L413"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_101
---

# sync_pending_orders_lifecycle()

## Connections
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[Any_41]] - `references` [EXTRACTED]
- [[Cancel stale or invalid bot-owned pending orders for one symbol.]] - `rationale_for` [EXTRACTED]
- [[CancelResult]] - `calls` [EXTRACTED]
- [[PendingScoreDecision]] - `uses` [INFERRED]
- [[TradeExecutor]] - `uses` [INFERRED]
- [[_build_pending_reentry_guard()]] - `calls` [EXTRACTED]
- [[_direction_from_type()]] - `calls` [EXTRACTED]
- [[_log_pending_score_guard_keep()]] - `calls` [EXTRACTED]
- [[_notify_pending_lifecycle_cancel()]] - `calls` [EXTRACTED]
- [[_pending_age_minutes()]] - `calls` [EXTRACTED]
- [[_pending_lifecycle_cancel_reason()]] - `calls` [EXTRACTED]
- [[_signal_normalized_score()]] - `calls` [EXTRACTED]
- [[format_price()]] - `calls` [EXTRACTED]
- [[get_bot_pending_orders()]] - `calls` [EXTRACTED]
- [[pending_order_manager.py]] - `contains` [EXTRACTED]
- [[run_cycle()]] - `calls` [EXTRACTED]
- [[test_buy_limit_cancelled_if_price_rises_too_far_from_entry()]] - `calls` [EXTRACTED]
- [[test_cancelled_score_drop_is_recorded_in_reentry_guard()]] - `calls` [EXTRACTED]
- [[test_cancelled_when_direction_changes()]] - `calls` [EXTRACTED]
- [[test_cancelled_when_order_age_exceeds_expiration_minutes()]] - `calls` [EXTRACTED]
- [[test_cancelled_when_score_drops_below_keep_threshold()]] - `calls` [EXTRACTED]
- [[test_does_not_cancel_when_distance_is_inside_limit()]] - `calls` [EXTRACTED]
- [[test_execution_mode_safety.py]] - `imports` [EXTRACTED]
- [[test_manual_unknown_order_is_not_cancelled()]] - `calls` [EXTRACTED]
- [[test_no_trade_entries_written_for_cancelled_pending_order()]] - `calls` [EXTRACTED]
- [[test_pending_order_lifecycle.py]] - `imports` [EXTRACTED]
- [[test_pending_order_manager_logs_cancelled_only_after_success()]] - `calls` [EXTRACTED]
- [[test_pending_order_manager_records_cancel_failed_when_executor_fails()]] - `calls` [EXTRACTED]
- [[test_score_drop_cancels_after_required_confirmations()]] - `calls` [EXTRACTED]
- [[test_score_drop_inside_grace_does_not_cancel()]] - `calls` [EXTRACTED]
- [[test_score_drop_waiting_confirmation_does_not_cancel()]] - `calls` [EXTRACTED]
- [[test_sell_limit_cancelled_if_price_falls_too_far_from_entry()]] - `calls` [EXTRACTED]
- [[with_symbol_config()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_101