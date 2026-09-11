---
source_file: "Trading/001WM_STRATEGY_BOT/tests/test_pending_order_dedup.py"
type: "code"
community: "Community 109"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_109
---

# test_pending_order_dedup.py

## Connections
- [[ExecutionJournal]] - `imports` [EXTRACTED]
- [[FakeMT5Pending]] - `contains` [EXTRACTED]
- [[PendingReentryGuard]] - `imports` [EXTRACTED]
- [[TradeDirection]] - `imports` [EXTRACTED]
- [[TradeExecutor]] - `imports` [EXTRACTED]
- [[TradeRequest]] - `imports` [EXTRACTED]
- [[_order()_1]] - `contains` [EXTRACTED]
- [[_request()]] - `contains` [EXTRACTED]
- [[_settings()_2]] - `contains` [EXTRACTED]
- [[entry_from_journal_record()]] - `imports` [EXTRACTED]
- [[executionmodels.py]] - `imports_from` [EXTRACTED]
- [[execution_journal.py]] - `imports_from` [EXTRACTED]
- [[pending_order_manager.py]] - `imports_from` [EXTRACTED]
- [[pending_reentry_guard.py]] - `imports_from` [EXTRACTED]
- [[test_duplicate_alert_does_not_block_market_but_pending_validation_blocks_duplicate()]] - `contains` [EXTRACTED]
- [[test_execution_journal_records_pending_blocked()]] - `contains` [EXTRACTED]
- [[test_manual_pending_without_bot_ownership_is_ignored()]] - `contains` [EXTRACTED]
- [[test_no_order_send_when_pending_already_exists()]] - `contains` [EXTRACTED]
- [[test_no_pending_orders_allows_pending()]] - `contains` [EXTRACTED]
- [[test_pending_blocked_is_not_trade_entry()]] - `contains` [EXTRACTED]
- [[test_pending_inside_tolerance_blocks()]] - `contains` [EXTRACTED]
- [[test_pending_outside_tolerance_blocks_by_direction_limit()]] - `contains` [EXTRACTED]
- [[test_reentry_guard_allows_new_pending_when_score_improves()]] - `contains` [EXTRACTED]
- [[test_reentry_guard_blocks_new_pending_after_same_entry_cancellation()]] - `contains` [EXTRACTED]
- [[test_same_sell_limit_same_symbol_direction_entry_blocks()]] - `contains` [EXTRACTED]
- [[trade_entry_reconciler.py]] - `imports_from` [EXTRACTED]
- [[trade_executor.py]] - `imports_from` [EXTRACTED]
- [[validate_can_place_pending_order()]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_109