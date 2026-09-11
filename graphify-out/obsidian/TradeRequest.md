---
source_file: "Trading/001WM_STRATEGY_BOT/app/execution/models.py"
type: "code"
community: "Community 18"
location: "L57"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_18
---

# TradeRequest

## Connections
- [[dot-_base_record()]] - `references` [EXTRACTED]
- [[dot-_blocked_trade_result()]] - `references` [EXTRACTED]
- [[dot-_empty_trade_request()]] - `calls` [EXTRACTED]
- [[dot-_request()]] - `calls` [EXTRACTED]
- [[dot-_request()_1]] - `calls` [EXTRACTED]
- [[dot-_trade_request()]] - `calls` [EXTRACTED]
- [[dot-build_trade_request()]] - `calls` [EXTRACTED]
- [[dot-execute()]] - `references` [EXTRACTED]
- [[dot-execute_market_order()]] - `references` [EXTRACTED]
- [[dot-place_pending_limit_order()]] - `references` [EXTRACTED]
- [[dot-record_decision()]] - `references` [EXTRACTED]
- [[dot-test_allow_chasing_entry_in_demo_allows_with_warning()]] - `calls` [EXTRACTED]
- [[dot-test_buy_price_too_far_above_entry_blocks_execution()]] - `calls` [EXTRACTED]
- [[dot-test_buy_price_within_tolerance_allows_execution()]] - `calls` [EXTRACTED]
- [[dot-test_real_case_signal_4496_83_current_4489_93_blocks()]] - `calls` [EXTRACTED]
- [[dot-test_require_price_near_entry_disabled_allows_any_price()]] - `calls` [EXTRACTED]
- [[dot-test_required_journal_fields_are_present()]] - `calls` [EXTRACTED]
- [[dot-test_sell_price_too_far_below_entry_blocks_execution()]] - `calls` [EXTRACTED]
- [[dot-test_sell_price_within_tolerance_allows_execution()]] - `calls` [EXTRACTED]
- [[dot-test_trade_executor_uses_mocked_order_send()]] - `calls` [EXTRACTED]
- [[dot-to_record()_1]] - `method` [EXTRACTED]
- [[dot-validate()]] - `references` [EXTRACTED]
- [[dot-validate()_1]] - `references` [EXTRACTED]
- [[EntryProximityValidator]] - `uses` [INFERRED]
- [[ExecutionJournal]] - `uses` [INFERRED]
- [[RiskManager]] - `uses` [INFERRED]
- [[TestEntryProximityValidator]] - `uses` [INFERRED]
- [[TestExecutionJournal]] - `uses` [INFERRED]
- [[TestLegacyJournalShape]] - `uses` [INFERRED]
- [[TestPositionSizingAndExecutor]] - `uses` [INFERRED]
- [[TestTradeOutcomeTracker]] - `uses` [INFERRED]
- [[TradeExecutor]] - `uses` [INFERRED]
- [[TradeGuard]] - `uses` [INFERRED]
- [[Validated instruction to send a single MT5 market order.]] - `rationale_for` [EXTRACTED]
- [[_request()]] - `calls` [EXTRACTED]
- [[entry_proximity.py]] - `imports` [EXTRACTED]
- [[execution__init__.py]] - `imports` [EXTRACTED]
- [[executionmodels.py]] - `contains` [EXTRACTED]
- [[execution_journal.py]] - `imports` [EXTRACTED]
- [[risk_manager.py]] - `imports` [EXTRACTED]
- [[test_execution.py]] - `imports` [EXTRACTED]
- [[test_pending_allowed_if_retest_valid_and_structure_clear()]] - `calls` [EXTRACTED]
- [[test_pending_blocked_if_structure_unclear()]] - `calls` [EXTRACTED]
- [[test_pending_order_dedup.py]] - `imports` [EXTRACTED]
- [[test_structure_first.py]] - `imports` [EXTRACTED]
- [[test_trade_outcome_tracker.py]] - `imports` [EXTRACTED]
- [[trade_executor.py]] - `imports` [EXTRACTED]
- [[trade_guard.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_18