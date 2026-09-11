---
source_file: "Academia/Academy_Test/backend/app/api/v1/payments/router.py"
type: "code"
community: "Community 11"
location: "L1009"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_11
---

# upload_qr_image()

## Connections
- [[dot-update()]] - `calls` [INFERRED]
- [[AsyncSession]] - `references` [EXTRACTED]
- [[AuditService]] - `uses` [INFERRED]
- [[PaymentSettings]] - `uses` [INFERRED]
- [[PaymentSettingsResponse]] - `uses` [INFERRED]
- [[Request]] - `references` [EXTRACTED]
- [[Upload QR code image for payment settings.]] - `rationale_for` [EXTRACTED]
- [[UploadFile]] - `references` [EXTRACTED]
- [[_build_qr_url()]] - `calls` [EXTRACTED]
- [[_delete_qr_file_by_url()]] - `calls` [EXTRACTED]
- [[_get_payment_settings()]] - `calls` [EXTRACTED]
- [[_sanitize_filename()]] - `calls` [EXTRACTED]
- [[_validate_image_magic_bytes()]] - `calls` [EXTRACTED]
- [[_validate_svg_content()]] - `calls` [EXTRACTED]
- [[paymentsrouter.py]] - `contains` [EXTRACTED]
- [[post]] - `references` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_11