---
source_file: "Trading/001WM_STRATEGY_BOT/app/execution/pending_reentry_guard.py"
type: "code"
community: "Community 117"
location: "L38"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_117
---

# PendingReentryGuard

## Connections
- [[dot-__init__()_8]] - `method` [EXTRACTED]
- [[dot-_float()]] - `method` [EXTRACTED]
- [[dot-_latest_matching_cancelled()]] - `method` [EXTRACTED]
- [[dot-_load_state()]] - `method` [EXTRACTED]
- [[dot-_parse_dt()]] - `method` [EXTRACTED]
- [[dot-_resolve_path()]] - `method` [EXTRACTED]
- [[dot-_save_state()]] - `method` [EXTRACTED]
- [[dot-_utc()]] - `method` [EXTRACTED]
- [[dot-can_place_pending()]] - `method` [EXTRACTED]
- [[dot-record_pending_cancelled()]] - `method` [EXTRACTED]
- [[dot-record_pending_filled_or_removed()]] - `method` [EXTRACTED]
- [[dot-record_pending_placed()]] - `method` [EXTRACTED]
- [[dot-record_pending_seen()]] - `method` [EXTRACTED]
- [[dot-should_cancel_for_score_drop()]] - `method` [EXTRACTED]
- [[dot-sync_active_tickets()]] - `method` [EXTRACTED]
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[Persist pending stability state and prevent same-level re-entry churn.]] - `rationale_for` [EXTRACTED]
- [[_build_pending_reentry_guard()]] - `calls` [EXTRACTED]
- [[_guard()]] - `calls` [EXTRACTED]
- [[_handle_auto_execution()]] - `calls` [EXTRACTED]
- [[pending_order_manager.py]] - `imports` [EXTRACTED]
- [[pending_reentry_guard.py]] - `contains` [EXTRACTED]
- [[test_cancelled_score_drop_is_recorded_in_reentry_guard()]] - `calls` [EXTRACTED]
- [[test_pending_order_dedup.py]] - `imports` [EXTRACTED]
- [[test_pending_order_lifecycle.py]] - `imports` [EXTRACTED]
- [[test_pending_reentry_guard.py]] - `imports` [EXTRACTED]
- [[test_reentry_guard_allows_new_pending_when_score_improves()]] - `calls` [EXTRACTED]
- [[test_reentry_guard_blocks_new_pending_after_same_entry_cancellation()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_117