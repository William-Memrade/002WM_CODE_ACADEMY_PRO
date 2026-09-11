---
source_file: "Trading/001WM_STRATEGY_BOT/app/execution/pending_order_manager.py"
type: "code"
community: "Community 45"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_45
---

# pending_order_manager.py

## Connections
- [[001WM_STRATEGY_BOTappmain.py]] - `imports_from` [EXTRACTED]
- [[CancelResult]] - `contains` [EXTRACTED]
- [[Pending order management for safe cancellation during news blocks.]] - `rationale_for` [EXTRACTED]
- [[PendingOrderInfo]] - `contains` [EXTRACTED]
- [[PendingOrderMatch]] - `contains` [EXTRACTED]
- [[PendingReentryGuard]] - `imports` [EXTRACTED]
- [[PendingScoreDecision]] - `imports` [EXTRACTED]
- [[PendingValidationResult]] - `contains` [EXTRACTED]
- [[TradeExecutor]] - `imports` [EXTRACTED]
- [[TradeResult]] - `imports` [EXTRACTED]
- [[_build_pending_reentry_guard()]] - `contains` [EXTRACTED]
- [[_context_allows_direction()]] - `contains` [EXTRACTED]
- [[_direction_from_type()]] - `contains` [EXTRACTED]
- [[_is_bot_owned()]] - `contains` [EXTRACTED]
- [[_known_pending_tickets()]] - `contains` [EXTRACTED]
- [[_log_pending_score_guard_keep()]] - `contains` [EXTRACTED]
- [[_normalized_order_type()]] - `contains` [EXTRACTED]
- [[_notify_pending_lifecycle_cancel()]] - `contains` [EXTRACTED]
- [[_order_time_setup()]] - `contains` [EXTRACTED]
- [[_pending_age_minutes()]] - `contains` [EXTRACTED]
- [[_pending_lifecycle_cancel_reason()]] - `contains` [EXTRACTED]
- [[_pending_price_too_far()]] - `contains` [EXTRACTED]
- [[_request_normalized_score()]] - `contains` [EXTRACTED]
- [[_signal_direction()]] - `contains` [EXTRACTED]
- [[_signal_normalized_score()]] - `contains` [EXTRACTED]
- [[_type_name()]] - `contains` [EXTRACTED]
- [[_validate_pending_reentry_guard()]] - `contains` [EXTRACTED]
- [[cancel_duplicate_pending_orders()]] - `contains` [EXTRACTED]
- [[cancel_pending_orders_for_news()]] - `contains` [EXTRACTED]
- [[count_bot_pending_orders()]] - `contains` [EXTRACTED]
- [[datetime_22]] - `imports_from` [EXTRACTED]
- [[executionmodels.py]] - `imports_from` [EXTRACTED]
- [[format_price()]] - `imports` [EXTRACTED]
- [[get_bot_pending_orders()]] - `contains` [EXTRACTED]
- [[get_logger()]] - `imports` [EXTRACTED]
- [[get_open_pending_orders()]] - `contains` [EXTRACTED]
- [[has_equivalent_pending_order()]] - `contains` [EXTRACTED]
- [[logger.py]] - `imports_from` [EXTRACTED]
- [[pending_reentry_guard.py]] - `imports_from` [EXTRACTED]
- [[symbol_config.py]] - `imports_from` [EXTRACTED]
- [[sync_pending_orders_lifecycle()]] - `contains` [EXTRACTED]
- [[test_execution.py]] - `imports_from` [EXTRACTED]
- [[test_execution_mode_safety.py]] - `imports_from` [EXTRACTED]
- [[test_pending_order_dedup.py]] - `imports_from` [EXTRACTED]
- [[test_pending_order_lifecycle.py]] - `imports_from` [EXTRACTED]
- [[test_structure_first.py]] - `imports_from` [EXTRACTED]
- [[trade_executor.py]] - `imports_from` [EXTRACTED]
- [[validate_can_place_pending_order()]] - `contains` [EXTRACTED]
- [[with_symbol_config()]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_45