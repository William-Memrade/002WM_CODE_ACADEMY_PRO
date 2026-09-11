---
source_file: "Trading/001WM_STRATEGY_BOT/app/signals/status.py"
type: "code"
community: "Community 16"
location: "L17"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Community_16
---

# SignalStatus

## Connections
- [[dot-_header_for_status()]] - `references` [EXTRACTED]
- [[dot-_status_emoji()]] - `references` [EXTRACTED]
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[Enum]] - `inherits` [EXTRACTED]
- [[Operational status derived from normalized score and risk.]] - `rationale_for` [EXTRACTED]
- [[SignalFormatter]] - `uses` [INFERRED]
- [[TestAutoExecutionStatusGate]] - `uses` [INFERRED]
- [[TestNewsBlockedHighScore]] - `uses` [INFERRED]
- [[TestNewsBlockedLowScore]] - `uses` [INFERRED]
- [[TestNewsBlockedNeverCallsOrderSend]] - `uses` [INFERRED]
- [[TestSignalStatusClassification]] - `uses` [INFERRED]
- [[TestSignalStore]] - `uses` [INFERRED]
- [[_classification_with_status()]] - `uses` [INFERRED]
- [[_execution_candidate()]] - `uses` [INFERRED]
- [[_handle_auto_execution()]] - `uses` [INFERRED]
- [[_handle_news_blocked_execution()]] - `uses` [INFERRED]
- [[_log_score_classification()]] - `references` [EXTRACTED]
- [[_persist_classified_signal()]] - `uses` [INFERRED]
- [[_process_waiting_retests()]] - `uses` [INFERRED]
- [[classify_signal_status()]] - `references` [EXTRACTED]
- [[formatter.py]] - `imports` [EXTRACTED]
- [[run_cycle()]] - `uses` [INFERRED]
- [[status.py]] - `contains` [EXTRACTED]
- [[str]] - `inherits` [EXTRACTED]
- [[test_news_scoring_flow.py]] - `imports` [EXTRACTED]
- [[test_profile_block_does_not_promote_no_signal_to_execution_flow()]] - `uses` [INFERRED]
- [[test_profile_block_precedes_score_and_all_execution_components()]] - `uses` [INFERRED]
- [[test_score_guard_applies_when_profile_allows_but_score_is_low()]] - `uses` [INFERRED]
- [[test_signal_formatter_alert_does_not_send_telegram()]] - `uses` [INFERRED]
- [[test_signal_status.py]] - `imports` [EXTRACTED]
- [[test_signal_store.py]] - `imports` [EXTRACTED]
- [[test_strategy_profiles.py]] - `imports` [EXTRACTED]
- [[test_telegram_notifications.py]] - `imports` [EXTRACTED]
- [[test_unauthorized_symbol_exits_before_any_order_path()]] - `uses` [INFERRED]
- [[test_xau_allowed_at_existing_threshold_reaches_levels_and_risk()]] - `uses` [INFERRED]

#graphify/code #graphify/INFERRED #community/Community_16