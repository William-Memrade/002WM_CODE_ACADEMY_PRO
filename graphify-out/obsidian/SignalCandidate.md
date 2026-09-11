---
source_file: "Trading/001WM_STRATEGY_BOT/app/signals/scoring.py"
type: "code"
community: "Community 29"
location: "L65"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_29
---

# SignalCandidate

## Connections
- [[dot-_build_record()]] - `references` [EXTRACTED]
- [[dot-_create_mock_candidate()]] - `calls` [EXTRACTED]
- [[dot-_entry_atr()]] - `references` [EXTRACTED]
- [[dot-_entry_timeframe()]] - `references` [EXTRACTED]
- [[dot-_format_execution_levels_block()]] - `references` [EXTRACTED]
- [[dot-_format_primary_levels_block()]] - `references` [EXTRACTED]
- [[dot-_format_technical_levels_block()]] - `references` [EXTRACTED]
- [[dot-_format_timeframes()]] - `references` [EXTRACTED]
- [[dot-_get_dedup_key()]] - `references` [EXTRACTED]
- [[dot-_load_dedup_cache()]] - `calls` [EXTRACTED]
- [[dot-_risk_text()]] - `references` [EXTRACTED]
- [[dot-_run_auto()]] - `references` [EXTRACTED]
- [[dot-_setup_timeframe()]] - `references` [EXTRACTED]
- [[dot-_signal_id()]] - `references` [EXTRACTED]
- [[dot-_sl_distance()]] - `references` [EXTRACTED]
- [[dot-_tp_distance()]] - `references` [EXTRACTED]
- [[dot-build_trade_request()]] - `references` [EXTRACTED]
- [[dot-evaluate()]] - `calls` [EXTRACTED]
- [[dot-format_message()]] - `references` [EXTRACTED]
- [[dot-is_duplicate()]] - `references` [EXTRACTED]
- [[dot-save()]] - `references` [EXTRACTED]
- [[dot-validate()_3]] - `references` [EXTRACTED]
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[Output of the ScoringEngine, representing a potential signal candidate. This is…]] - `rationale_for` [EXTRACTED]
- [[RiskManager]] - `uses` [INFERRED]
- [[SignalFormatter]] - `uses` [INFERRED]
- [[SignalStore]] - `uses` [INFERRED]
- [[TestAutoExecutionStatusGate]] - `uses` [INFERRED]
- [[TestSignalCandidateIsAnalysisOnly]] - `uses` [INFERRED]
- [[TestSignalStore]] - `uses` [INFERRED]
- [[_blocked_levels()]] - `uses` [INFERRED]
- [[_build_first_valid_candidate()]] - `uses` [INFERRED]
- [[_build_from_dataframe()]] - `uses` [INFERRED]
- [[_candidate()]] - `calls` [EXTRACTED]
- [[_candidate()_2]] - `calls` [EXTRACTED]
- [[_candidate()_1]] - `calls` [EXTRACTED]
- [[_dispatch_alert()]] - `uses` [INFERRED]
- [[_execution_candidate()]] - `calls` [EXTRACTED]
- [[_handle_auto_execution()]] - `uses` [INFERRED]
- [[_handle_news_blocked_execution()]] - `uses` [INFERRED]
- [[_log_score_classification()]] - `uses` [INFERRED]
- [[_persist_classified_signal()]] - `uses` [INFERRED]
- [[_process_news_wait_revalidation()]] - `uses` [INFERRED]
- [[_process_waiting_retests()]] - `uses` [INFERRED]
- [[_sync_candidate_from_trade_request()]] - `uses` [INFERRED]
- [[build_execution_levels()]] - `uses` [INFERRED]
- [[candidate_to_record()]] - `uses` [INFERRED]
- [[classify_signal()]] - `uses` [INFERRED]
- [[classify_signal_status()]] - `uses` [INFERRED]
- [[execution_levels.py]] - `imports` [EXTRACTED]
- [[formatter.py]] - `imports` [EXTRACTED]
- [[montgomery_backtest.py]] - `imports` [EXTRACTED]
- [[normalized_score()]] - `uses` [INFERRED]
- [[risk_level_from_candidate()]] - `uses` [INFERRED]
- [[risk_manager.py]] - `imports` [EXTRACTED]
- [[scoring.py]] - `contains` [EXTRACTED]
- [[signal_store.py]] - `imports` [EXTRACTED]
- [[signals__init__.py]] - `imports` [EXTRACTED]
- [[status.py]] - `imports` [EXTRACTED]
- [[test_execution.py]] - `imports` [EXTRACTED]
- [[test_security_no_trading.py]] - `imports` [EXTRACTED]
- [[test_signal_formatter_alert_does_not_send_telegram()]] - `calls` [EXTRACTED]
- [[test_signal_status.py]] - `imports` [EXTRACTED]
- [[test_signal_store.py]] - `imports` [EXTRACTED]
- [[test_strategy_profiles.py]] - `imports` [EXTRACTED]
- [[test_symbol_config.py]] - `imports` [EXTRACTED]
- [[test_telegram_notifications.py]] - `imports` [EXTRACTED]
- [[test_unauthorized_symbol_exits_before_any_order_path()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_29