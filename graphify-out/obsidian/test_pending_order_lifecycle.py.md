---
source_file: "Trading/001WM_STRATEGY_BOT/tests/test_pending_order_lifecycle.py"
type: "code"
community: "Community 101"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_101
---

# test_pending_order_lifecycle.py

## Connections
- [[ExecutionJournal]] - `imports` [EXTRACTED]
- [[FakeMT5]] - `contains` [EXTRACTED]
- [[PendingReentryGuard]] - `imports` [EXTRACTED]
- [[SpyExecutor]] - `contains` [EXTRACTED]
- [[TradeExecutor]] - `imports` [EXTRACTED]
- [[_journal()]] - `contains` [EXTRACTED]
- [[_order()]] - `contains` [EXTRACTED]
- [[_settings()_1]] - `contains` [EXTRACTED]
- [[execution_journal.py]] - `imports_from` [EXTRACTED]
- [[pending_order_manager.py]] - `imports_from` [EXTRACTED]
- [[pending_reentry_guard.py]] - `imports_from` [EXTRACTED]
- [[sync_pending_orders_lifecycle()]] - `imports` [EXTRACTED]
- [[test_buy_limit_cancelled_if_price_rises_too_far_from_entry()]] - `contains` [EXTRACTED]
- [[test_cancelled_score_drop_is_recorded_in_reentry_guard()]] - `contains` [EXTRACTED]
- [[test_cancelled_when_direction_changes()]] - `contains` [EXTRACTED]
- [[test_cancelled_when_order_age_exceeds_expiration_minutes()]] - `contains` [EXTRACTED]
- [[test_cancelled_when_score_drops_below_keep_threshold()]] - `contains` [EXTRACTED]
- [[test_does_not_cancel_when_distance_is_inside_limit()]] - `contains` [EXTRACTED]
- [[test_manual_unknown_order_is_not_cancelled()]] - `contains` [EXTRACTED]
- [[test_no_trade_entries_written_for_cancelled_pending_order()]] - `contains` [EXTRACTED]
- [[test_score_drop_cancels_after_required_confirmations()]] - `contains` [EXTRACTED]
- [[test_score_drop_inside_grace_does_not_cancel()]] - `contains` [EXTRACTED]
- [[test_score_drop_waiting_confirmation_does_not_cancel()]] - `contains` [EXTRACTED]
- [[test_sell_limit_cancelled_if_price_falls_too_far_from_entry()]] - `contains` [EXTRACTED]
- [[trade_executor.py]] - `imports_from` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_101