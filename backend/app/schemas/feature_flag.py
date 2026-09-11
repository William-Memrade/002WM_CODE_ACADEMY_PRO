"""
CodeAcademy Pro — Pydantic Schemas: Feature Flags
"""

from pydantic import BaseModel


class FeatureFlagResponse(BaseModel):
    """Feature flag in list responses."""
    id: str
    key: str
    enabled: bool
    description: str | None


class FeatureFlagToggleRequest(BaseModel):
    """PATCH /admin/feature-flags/{key} request body."""
    enabled: bool
