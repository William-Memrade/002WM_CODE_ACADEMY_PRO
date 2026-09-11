"""
CodeAcademy Pro — Settings Router
Admin endpoints for platform general settings (key-value system_settings table).
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.rls import get_rls_db
from app.middlewares.rbac import require_admin
from app.models.system import SystemSetting
from app.core.config import get_settings as get_app_settings
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest
from app.services.audit_service import AuditService

router = APIRouter()

# Key mapping between API field names and DB keys
_SETTING_KEYS = {
    "platform_name": "app_name",
    "default_currency": "default_currency",
    "global_max_students_per_class": "global_max_students_per_class",
}

# Currency code → display symbol (disambiguated for LATAM)
_CURRENCY_SYMBOLS = {
    "USD": "US$",
    "EUR": "€",
    "MXN": "MX$",
    "COP": "COP$",
    "GTQ": "Q",
    "HNL": "L",
    "NIO": "C$",
    "CRC": "₡",
    "SVC": "$",
}


def _get_currency_symbol(code: str) -> str:
    return _CURRENCY_SYMBOLS.get(code, code)


async def _load_settings(db: AsyncSession) -> dict:
    """Load relevant system_settings rows into a dict."""
    result = await db.execute(
        select(SystemSetting).where(
            SystemSetting.key.in_(list(_SETTING_KEYS.values()))
        )
    )
    rows = {r.key: r.value for r in result.scalars().all()}
    return rows


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Get general platform settings. Admin only."""
    rows = await _load_settings(db)
    app_name = get_app_settings().APP_NAME
    return SettingsResponse(
        platform_name=rows.get("app_name", app_name),
        default_currency=rows.get("default_currency", "USD"),
        global_max_students_per_class=int(rows.get("global_max_students_per_class", "100")),
    )


@router.get("/public")
async def get_public_settings(db: AsyncSession = Depends(get_db)):
    """Get public platform settings (platform name, currency, global max). No auth required."""
    result = await db.execute(
        select(SystemSetting).where(
            SystemSetting.key.in_(["app_name", "default_currency", "global_max_students_per_class"]),
            SystemSetting.is_public == True,
        )
    )
    rows = {r.key: r.value for r in result.scalars().all()}
    app_name = get_app_settings().APP_NAME
    currency = rows.get("default_currency", "USD")
    return {
        "platform_name": rows.get("app_name", app_name),
        "default_currency": currency,
        "currency_symbol": _get_currency_symbol(currency),
        "global_max_students_per_class": int(rows.get("global_max_students_per_class", "100")),
    }


@router.put("", response_model=SettingsResponse)
async def update_settings(
    body: SettingsUpdateRequest,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Update general platform settings. Admin only."""
    changed = []

    # Load existing rows
    rows = await _load_settings(db)

    # Update / create each field
    if body.platform_name is not None:
        key = _SETTING_KEYS["platform_name"]
        val = body.platform_name
        if key in rows:
            await db.execute(update(SystemSetting).where(SystemSetting.key == key).values(value=val))
        else:
            await db.execute(insert(SystemSetting).values(key=key, value=val, description="Platform name", is_public=True))
        rows[key] = val
        changed.append("platform_name")

    if body.default_currency is not None:
        key = _SETTING_KEYS["default_currency"]
        val = body.default_currency
        if key in rows:
            await db.execute(update(SystemSetting).where(SystemSetting.key == key).values(value=val))
        else:
            await db.execute(insert(SystemSetting).values(key=key, value=val, description="Default currency", is_public=True))
        rows[key] = val
        changed.append("default_currency")

    if body.global_max_students_per_class is not None:
        key = _SETTING_KEYS["global_max_students_per_class"]
        val = str(body.global_max_students_per_class)
        if key in rows:
            await db.execute(update(SystemSetting).where(SystemSetting.key == key).values(value=val))
        else:
            await db.execute(insert(SystemSetting).values(key=key, value=val, description="Global max students per class", is_public=True))
        rows[key] = val
        changed.append("global_max_students_per_class")

    await db.commit()

    # Audit
    if changed:
        await AuditService(db).log_action(
            actor_user=current_user,
            action="settings_updated",
            entity_type="system_setting",
            request=request,
            metadata={"changed_fields": changed},
        )

    # Build response from in-memory updated values
    app_name = get_app_settings().APP_NAME
    return SettingsResponse(
        platform_name=rows.get("app_name", app_name),
        default_currency=rows.get("default_currency", "USD"),
        global_max_students_per_class=int(rows.get("global_max_students_per_class", "100")),
    )
