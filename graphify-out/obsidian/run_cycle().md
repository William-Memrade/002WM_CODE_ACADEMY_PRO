---
source_file: "Trading/001WM_STRATEGY_BOT/app/main.py"
type: "code"
community: "Community 16"
location: "L1802"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_16
---

# run_cycle()

## Connections
- [[dot-format_message()]] - `calls` [EXTRACTED]
- [[dot-test_no_signal_not_persisted_when_disabled()]] - `calls` [EXTRACTED]
- [[dot-test_signal_store_duplicate_does_not_block_execution_evaluation()]] - `calls` [EXTRACTED]
- [[dot-test_watchlist_persisted_but_not_written_to_execution_journal()]] - `calls` [EXTRACTED]
- [[001WM_STRATEGY_BOTappmain.py]] - `contains` [EXTRACTED]
- [[ActiveTradeManager]] - `calls` [EXTRACTED]
- [[Executes one full analysis cycle across all configured symbols. For each…]] - `rationale_for` [EXTRACTED]
- [[ExecutionJournal]] - `calls` [EXTRACTED]
- [[NewsFilter]] - `uses` [INFERRED]
- [[PendingSetupStore]] - `calls` [EXTRACTED]
- [[ScoringEngine]] - `uses` [INFERRED]
- [[SignalFormatter]] - `uses` [INFERRED]
- [[SignalStatus]] - `uses` [INFERRED]
- [[SignalStore]] - `uses` [INFERRED]
- [[TelegramNotifier]] - `uses` [INFERRED]
- [[TradeExecutor]] - `calls` [EXTRACTED]
- [[TradeOutcomeTracker]] - `calls` [EXTRACTED]
- [[_analyse_symbol()]] - `calls` [EXTRACTED]
- [[_classification_with_status()]] - `calls` [EXTRACTED]
- [[_dispatch_alert()]] - `calls` [EXTRACTED]
- [[_get_telegram_notifier()]] - `calls` [EXTRACTED]
- [[_handle_auto_execution()]] - `calls` [EXTRACTED]
- [[_is_duplicate()]] - `calls` [EXTRACTED]
- [[_persist_classified_signal()]] - `calls` [EXTRACTED]
- [[_process_news_wait_revalidation()]] - `calls` [EXTRACTED]
- [[_process_waiting_retests()]] - `calls` [EXTRACTED]
- [[_record_signal()]] - `calls` [EXTRACTED]
- [[_send_execution_telegram()]] - `calls` [EXTRACTED]
- [[_settings_overlay()]] - `calls` [EXTRACTED]
- [[classify_signal()]] - `calls` [EXTRACTED]
- [[clear_logs_on_new_day()]] - `calls` [EXTRACTED]
- [[is_auto_trading_enabled_for_symbol()]] - `calls` [EXTRACTED]
- [[main()_13]] - `calls` [EXTRACTED]
- [[maybe_cleanup_logs()]] - `calls` [EXTRACTED]
- [[rebuild_trade_entries_from_journal_and_mt5()]] - `calls` [EXTRACTED]
- [[recover_orphan_positions()]] - `calls` [EXTRACTED]
- [[strategy_settings()]] - `calls` [EXTRACTED]
- [[sync_pending_orders_lifecycle()]] - `calls` [EXTRACTED]
- [[test_execution.py]] - `imports` [EXTRACTED]
- [[test_profile_block_does_not_promote_no_signal_to_execution_flow()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_16