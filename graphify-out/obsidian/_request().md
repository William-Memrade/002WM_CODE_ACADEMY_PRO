---
source_file: "Trading/001WM_STRATEGY_BOT/tests/test_pending_order_dedup.py"
type: "code"
community: "Community 109"
location: "L80"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_109
---

# _request()

## Connections
- [[TradeDirection]] - `uses` [INFERRED]
- [[TradeRequest]] - `calls` [EXTRACTED]
- [[test_duplicate_alert_does_not_block_market_but_pending_validation_blocks_duplicate()]] - `calls` [EXTRACTED]
- [[test_manual_pending_without_bot_ownership_is_ignored()]] - `calls` [EXTRACTED]
- [[test_no_order_send_when_pending_already_exists()]] - `calls` [EXTRACTED]
- [[test_no_pending_orders_allows_pending()]] - `calls` [EXTRACTED]
- [[test_pending_inside_tolerance_blocks()]] - `calls` [EXTRACTED]
- [[test_pending_order_dedup.py]] - `contains` [EXTRACTED]
- [[test_pending_outside_tolerance_blocks_by_direction_limit()]] - `calls` [EXTRACTED]
- [[test_reentry_guard_allows_new_pending_when_score_improves()]] - `calls` [EXTRACTED]
- [[test_reentry_guard_blocks_new_pending_after_same_entry_cancellation()]] - `calls` [EXTRACTED]
- [[test_same_sell_limit_same_symbol_direction_entry_blocks()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_109