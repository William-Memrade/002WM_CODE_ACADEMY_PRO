---
source_file: "Trading/001WM_STRATEGY_BOT/app/main.py"
type: "code"
community: "Community 16"
location: "L2335"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_16
---

# main()

## Connections
- [[001WM_STRATEGY_BOTappmain.py]] - `contains` [EXTRACTED]
- [[Entry point for the XAU Signal Bot. Handles argument parsing, MT5 connection…]] - `rationale_for` [EXTRACTED]
- [[ExecutionJournal]] - `calls` [EXTRACTED]
- [[MT5ConnectionManager]] - `calls` [EXTRACTED]
- [[Path_8]] - `calls` [EXTRACTED]
- [[PendingSetupStore]] - `calls` [EXTRACTED]
- [[ScoringEngine]] - `calls` [EXTRACTED]
- [[SignalStore]] - `calls` [EXTRACTED]
- [[TelegramNotifier]] - `calls` [EXTRACTED]
- [[TradeExecutor]] - `calls` [EXTRACTED]
- [[_build_news_filter()]] - `calls` [EXTRACTED]
- [[_get_mt5_server_time()]] - `calls` [EXTRACTED]
- [[_handle_sigint()]] - `indirect_call` [INFERRED]
- [[_parse_args()]] - `calls` [EXTRACTED]
- [[_print_banner()]] - `calls` [EXTRACTED]
- [[_record_startup_timestamp()]] - `calls` [EXTRACTED]
- [[_reset_all_data()]] - `calls` [EXTRACTED]
- [[_restart_recover_from_mt5()]] - `calls` [EXTRACTED]
- [[_run_auto_learning_engine()]] - `calls` [EXTRACTED]
- [[cancel_duplicate_pending_orders()]] - `calls` [EXTRACTED]
- [[check_symbol_exists()]] - `calls` [EXTRACTED]
- [[rebuild_trade_entries_from_journal_and_mt5()]] - `calls` [EXTRACTED]
- [[reconstruct_journal_from_mt5()]] - `calls` [EXTRACTED]
- [[recover_orphan_positions()]] - `calls` [EXTRACTED]
- [[run_cycle()]] - `calls` [EXTRACTED]
- [[start_metrics_server()]] - `calls` [EXTRACTED]
- [[sync_all_open_positions_to_grafana()]] - `calls` [EXTRACTED]
- [[test_profile_block_does_not_promote_no_signal_to_execution_flow()]] - `indirect_call` [INFERRED]
- [[test_profile_block_precedes_score_and_all_execution_components()]] - `indirect_call` [INFERRED]
- [[test_score_guard_applies_when_profile_allows_but_score_is_low()]] - `indirect_call` [INFERRED]
- [[test_unauthorized_symbol_exits_before_any_order_path()]] - `indirect_call` [INFERRED]
- [[test_xau_allowed_at_existing_threshold_reaches_levels_and_risk()]] - `indirect_call` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/Community_16