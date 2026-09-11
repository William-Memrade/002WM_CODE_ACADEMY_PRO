---
source_file: "Trading/001WM_STRATEGY_BOT/app/execution/pending_order_manager.py"
type: "code"
community: "Community 109"
location: "L225"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_109
---

# validate_can_place_pending_order()

## Connections
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[Any_41]] - `references` [EXTRACTED]
- [[PendingValidationResult]] - `calls` [EXTRACTED]
- [[Validate that placing this pending order would not duplicate an existing one.]] - `rationale_for` [EXTRACTED]
- [[_direction_from_type()]] - `calls` [EXTRACTED]
- [[_handle_auto_execution()]] - `calls` [EXTRACTED]
- [[_validate_pending_reentry_guard()]] - `calls` [EXTRACTED]
- [[count_bot_pending_orders()]] - `calls` [EXTRACTED]
- [[get_bot_pending_orders()]] - `calls` [EXTRACTED]
- [[has_equivalent_pending_order()]] - `calls` [EXTRACTED]
- [[pending_order_manager.py]] - `contains` [EXTRACTED]
- [[test_duplicate_alert_does_not_block_market_but_pending_validation_blocks_duplicate()]] - `calls` [EXTRACTED]
- [[test_manual_pending_without_bot_ownership_is_ignored()]] - `calls` [EXTRACTED]
- [[test_no_order_send_when_pending_already_exists()]] - `calls` [EXTRACTED]
- [[test_no_pending_orders_allows_pending()]] - `calls` [EXTRACTED]
- [[test_pending_allowed_if_retest_valid_and_structure_clear()]] - `calls` [EXTRACTED]
- [[test_pending_blocked_if_structure_unclear()]] - `calls` [EXTRACTED]
- [[test_pending_inside_tolerance_blocks()]] - `calls` [EXTRACTED]
- [[test_pending_order_dedup.py]] - `imports` [EXTRACTED]
- [[test_pending_outside_tolerance_blocks_by_direction_limit()]] - `calls` [EXTRACTED]
- [[test_reentry_guard_allows_new_pending_when_score_improves()]] - `calls` [EXTRACTED]
- [[test_reentry_guard_blocks_new_pending_after_same_entry_cancellation()]] - `calls` [EXTRACTED]
- [[test_same_sell_limit_same_symbol_direction_entry_blocks()]] - `calls` [EXTRACTED]
- [[test_structure_first.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_109