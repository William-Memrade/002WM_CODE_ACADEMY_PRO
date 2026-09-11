---
type: community
cohesion: 0.03
members: 112
---

# Community 7

**Cohesion:** 0.03 - loosely connected
**Members:** 112 nodes

## Members
- [[NOTE echo is ALWAYS False for performance. Use SQL logging middleware for…]] - rationale - Academia/Academy_Test/backend/app/db/session.py
- [[NOTE static paths MUST be registered before dynamic {class_id} routes]] - rationale - Academia/Academy_Test/backend/app/api/v1/course_classes/router.py
- [[dot-__init__()_96]] - code - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[dot-get_all()_1]] - code - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[dot-invalidate_cache()]] - code - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[dot-is_enabled()]] - code - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[dot-toggle()]] - code - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[Apply 'system' RLS context to an existing session. Used by the ARQ worker and…]] - rationale - Academia/Academy_Test/backend/app/db/rls.py
- [[Apply RLS context to an existing session. Callable from any async context…]] - rationale - Academia/Academy_Test/backend/app/db/rls.py
- [[AsyncSession_20]] - code
- [[AsyncSession_21]] - code
- [[AsyncSession_22]] - code
- [[AsyncSession_23]] - code
- [[AsyncSession_24]] - code
- [[AsyncSession_25]] - code
- [[AuditLogListResponse]] - code - Academia/Academy_Test/backend/app/schemas/audit.py
- [[AuditLogResponse]] - code - Academia/Academy_Test/backend/app/schemas/audit.py
- [[Cached settings instance (singleton).]] - rationale - Academia/Academy_Test/backend/app/core/config.py
- [[Check if a feature flag is enabled. Uses Redis cache first, falls back to…]] - rationale - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[CodeAcademy Pro — API v1 Router Aggregates all domain routers under apiv1.]] - rationale - Academia/Academy_Test/backend/app/api/v1/router.py
- [[CodeAcademy Pro — Admin Router Endpoints for admin-only operations feature…]] - rationale - Academia/Academy_Test/backend/app/api/v1/admin/router.py
- [[CodeAcademy Pro — Audit Logs Router (real) Admin-only endpoint for querying…]] - rationale - Academia/Academy_Test/backend/app/api/v1/audit/router.py
- [[CodeAcademy Pro — Audit Schemas Pydantic models for audit log responses.]] - rationale - Academia/Academy_Test/backend/app/schemas/audit.py
- [[CodeAcademy Pro — Audit Service Centralised, safe audit logging with IP  UA…]] - rationale - Academia/Academy_Test/backend/app/services/audit_service.py
- [[CodeAcademy Pro — Auth Router Registration, login, token refresh, profile.]] - rationale - Academia/Academy_Test/backend/app/api/v1/auth/router.py
- [[CodeAcademy Pro — Course Classes Router Endpoints for managing course…]] - rationale - Academia/Academy_Test/backend/app/api/v1/course_classes/router.py
- [[CodeAcademy Pro — Database Session Async SQLAlchemy engine and session factory.]] - rationale - Academia/Academy_Test/backend/app/db/session.py
- [[CodeAcademy Pro — Feature Flag Dependency FastAPI dependencies for gating…]] - rationale - Academia/Academy_Test/backend/app/middlewares/feature_flags.py
- [[CodeAcademy Pro — Feature Flags Service Database-backed feature flags with…]] - rationale - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[CodeAcademy Pro — JWT Authentication Middleware Extracts and validates JWT from…]] - rationale - Academia/Academy_Test/backend/app/middlewares/auth.py
- [[CodeAcademy Pro — Pydantic Schemas Feature Flags]] - rationale - Academia/Academy_Test/backend/app/schemas/feature_flag.py
- [[CodeAcademy Pro — RBAC (Role-Based Access Control) Middleware Role checking…]] - rationale - Academia/Academy_Test/backend/app/middlewares/rbac.py
- [[CodeAcademy Pro — RLS-Aware Database Session Provides FastAPI dependencies that…]] - rationale - Academia/Academy_Test/backend/app/db/rls.py
- [[CodeAcademy Pro — Redis Client Helper Provides a shared async Redis client…]] - rationale - Academia/Academy_Test/backend/app/core/redis_client.py
- [[CodeAcademy Pro — Settings Router Admin endpoints for platform general settings…]] - rationale - Academia/Academy_Test/backend/app/api/v1/settings/router.py
- [[Create a course review (student).]] - rationale - Academia/Academy_Test/backend/app/api/v1/reviews/router.py
- [[Dependency that checks if the current user has at least one of the required…]] - rationale - Academia/Academy_Test/backend/app/middlewares/rbac.py
- [[Determine the highest-priority role for RLS context. Priority admin  teacher…]] - rationale - Academia/Academy_Test/backend/app/db/rls.py
- [[Ensure user is active and not blocked.]] - rationale - Academia/Academy_Test/backend/app/middlewares/auth.py
- [[Extract and validate JWT token, return the current user. Raises 401 if token is…]] - rationale - Academia/Academy_Test/backend/app/middlewares/auth.py
- [[FastAPI dependency that yields an async database session. Automatically commits…]] - rationale - Academia/Academy_Test/backend/app/db/session.py
- [[FastAPI dependency returns the DB session with RLS context applied. The…]] - rationale - Academia/Academy_Test/backend/app/db/rls.py
- [[Feature flag evaluation with Redis cache. Falls back to DB when Redis is down.]] - rationale - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[Feature flag in list responses.]] - rationale - Academia/Academy_Test/backend/app/schemas/feature_flag.py
- [[FeatureFlagResponse]] - code - Academia/Academy_Test/backend/app/schemas/feature_flag.py
- [[FeatureFlagService]] - code - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[FeatureFlagToggleRequest]] - code - Academia/Academy_Test/backend/app/schemas/feature_flag.py
- [[Get all feature flags.]] - rationale - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[Get paginated audit logs (admin only).]] - rationale - Academia/Academy_Test/backend/app/api/v1/audit/router.py
- [[Invalidate cache for a specific flag.]] - rationale - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[Like get_rls_db but for endpoints with optional authentication. If no user is…]] - rationale - Academia/Academy_Test/backend/app/db/rls.py
- [[List all feature flags. Admin only.]] - rationale - Academia/Academy_Test/backend/app/api/v1/admin/router.py
- [[Mark all notifications as read.]] - rationale - Academia/Academy_Test/backend/app/api/v1/notifications/router.py
- [[Mark notification as read.]] - rationale - Academia/Academy_Test/backend/app/api/v1/notifications/router.py
- [[Notifications router.]] - rationale - Academia/Academy_Test/backend/app/api/v1/notifications/router.py
- [[Optional authentication — returns None if no token provided.]] - rationale - Academia/Academy_Test/backend/app/middlewares/auth.py
- [[PATCH adminfeature-flags{key} request body.]] - rationale - Academia/Academy_Test/backend/app/schemas/feature_flag.py
- [[Paginated audit log list response.]] - rationale - Academia/Academy_Test/backend/app/schemas/audit.py
- [[RLS context for background workers  system operations. Sets role to 'system'…]] - rationale - Academia/Academy_Test/backend/app/db/rls.py
- [[Redis]] - code
- [[Redis_1]] - code
- [[Request_14]] - code
- [[Return a FastAPI dependency that blocks access when a feature flag is disabled.]] - rationale - Academia/Academy_Test/backend/app/middlewares/feature_flags.py
- [[Return a new Redis client from the configured URL.]] - rationale - Academia/Academy_Test/backend/app/core/redis_client.py
- [[Set transaction-local variables for RLS. Uses set_config() instead of SET LOCAL…]] - rationale - Academia/Academy_Test/backend/app/db/rls.py
- [[Single audit log entry response.]] - rationale - Academia/Academy_Test/backend/app/schemas/audit.py
- [[Toggle a feature flag. Admin only.]] - rationale - Academia/Academy_Test/backend/app/api/v1/admin/router.py
- [[Toggle a feature flag. Returns True if flag was found and updated.]] - rationale - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[UUID_17]] - code
- [[Verify that the current user owns the resource. Admins bypass ownership check…]] - rationale - Academia/Academy_Test/backend/app/middlewares/rbac.py
- [[_apply_rls_context()]] - code - Academia/Academy_Test/backend/app/db/rls.py
- [[_get_primary_role()]] - code - Academia/Academy_Test/backend/app/db/rls.py
- [[adminrouter.py]] - code - Academia/Academy_Test/backend/app/api/v1/admin/router.py
- [[apply_rls_context_raw()]] - code - Academia/Academy_Test/backend/app/db/rls.py
- [[apply_system_rls_context()]] - code - Academia/Academy_Test/backend/app/db/rls.py
- [[auditrouter.py]] - code - Academia/Academy_Test/backend/app/api/v1/audit/router.py
- [[audit_service.py]] - code - Academia/Academy_Test/backend/app/services/audit_service.py
- [[authrouter.py]] - code - Academia/Academy_Test/backend/app/api/v1/auth/router.py
- [[course_classesrouter.py]] - code - Academia/Academy_Test/backend/app/api/v1/course_classes/router.py
- [[create_review()]] - code - Academia/Academy_Test/backend/app/api/v1/reviews/router.py
- [[datetime_28]] - code
- [[feature_flag.py]] - code - Academia/Academy_Test/backend/app/schemas/feature_flag.py
- [[get_audit_logs()]] - code - Academia/Academy_Test/backend/app/api/v1/audit/router.py
- [[get_current_active_user()]] - code - Academia/Academy_Test/backend/app/middlewares/auth.py
- [[get_current_user()_1]] - code - Academia/Academy_Test/backend/app/middlewares/auth.py
- [[get_db()]] - code - Academia/Academy_Test/backend/app/db/session.py
- [[get_optional_user()]] - code - Academia/Academy_Test/backend/app/middlewares/auth.py
- [[get_redis_client()]] - code - Academia/Academy_Test/backend/app/core/redis_client.py
- [[get_rls_db()]] - code - Academia/Academy_Test/backend/app/db/rls.py
- [[get_rls_db_optional()]] - code - Academia/Academy_Test/backend/app/db/rls.py
- [[get_settings()_1]] - code - Academia/Academy_Test/backend/app/core/config.py
- [[get_system_rls_db()]] - code - Academia/Academy_Test/backend/app/db/rls.py
- [[list_feature_flags()]] - code - Academia/Academy_Test/backend/app/api/v1/admin/router.py
- [[mark_all_read()]] - code - Academia/Academy_Test/backend/app/api/v1/notifications/router.py
- [[mark_read()]] - code - Academia/Academy_Test/backend/app/api/v1/notifications/router.py
- [[middlewaresauth.py]] - code - Academia/Academy_Test/backend/app/middlewares/auth.py
- [[middlewaresfeature_flags.py]] - code - Academia/Academy_Test/backend/app/middlewares/feature_flags.py
- [[notificationsrouter.py]] - code - Academia/Academy_Test/backend/app/api/v1/notifications/router.py
- [[post_10]] - code
- [[rbac.py]] - code - Academia/Academy_Test/backend/app/middlewares/rbac.py
- [[redis_client.py]] - code - Academia/Academy_Test/backend/app/core/redis_client.py
- [[require_feature_flag()]] - code - Academia/Academy_Test/backend/app/middlewares/feature_flags.py
- [[require_roles()]] - code - Academia/Academy_Test/backend/app/middlewares/rbac.py
- [[reviewsrouter.py]] - code - Academia/Academy_Test/backend/app/api/v1/reviews/router.py
- [[rls.py]] - code - Academia/Academy_Test/backend/app/db/rls.py
- [[schemasaudit.py]] - code - Academia/Academy_Test/backend/app/schemas/audit.py
- [[servicesfeature_flags.py]] - code - Academia/Academy_Test/backend/app/services/feature_flags.py
- [[session.py]] - code - Academia/Academy_Test/backend/app/db/session.py
- [[settingsrouter.py]] - code - Academia/Academy_Test/backend/app/api/v1/settings/router.py
- [[toggle_feature_flag()]] - code - Academia/Academy_Test/backend/app/api/v1/admin/router.py
- [[v1router.py]] - code - Academia/Academy_Test/backend/app/api/v1/router.py
- [[verify_ownership()]] - code - Academia/Academy_Test/backend/app/middlewares/rbac.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_7
SORT file.name ASC
```

## Connections to other communities
- 30 edges to [[_COMMUNITY_Community 4]]
- 19 edges to [[_COMMUNITY_Community 25]]
- 17 edges to [[_COMMUNITY_Community 12]]
- 12 edges to [[_COMMUNITY_Community 11]]
- 11 edges to [[_COMMUNITY_Community 33]]
- 10 edges to [[_COMMUNITY_Community 14]]
- 8 edges to [[_COMMUNITY_Community 65]]
- 7 edges to [[_COMMUNITY_Community 96]]
- 5 edges to [[_COMMUNITY_Community 68]]
- 4 edges to [[_COMMUNITY_Community 6]]
- 4 edges to [[_COMMUNITY_Community 54]]
- 3 edges to [[_COMMUNITY_Community 10]]
- 3 edges to [[_COMMUNITY_Community 83]]
- 2 edges to [[_COMMUNITY_Community 164]]
- 2 edges to [[_COMMUNITY_Community 169]]
- 1 edge to [[_COMMUNITY_Community 197]]
- 1 edge to [[_COMMUNITY_Community 189]]
- 1 edge to [[_COMMUNITY_Community 251]]

## Top bridge nodes
- [[audit_service.py]] - degree 22, connects to 7 communities
- [[get_settings()_1]] - degree 18, connects to 6 communities
- [[course_classesrouter.py]] - degree 31, connects to 5 communities
- [[session.py]] - degree 18, connects to 5 communities
- [[authrouter.py]] - degree 25, connects to 4 communities