# Row Level Security (RLS) — Technical Guide

## Overview

CodeAcademy Pro uses PostgreSQL Row Level Security to enforce data isolation **at the database level**. This is a defense-in-depth layer that works alongside FastAPI's RBAC middleware. Even if an endpoint vulnerability bypasses application-level checks, RLS prevents unauthorized data access.

## What RLS Protects

| Protection Level | Tables | What it prevents |
|-----------------|--------|------------------|
| **Critical** | `payments`, `payment_proofs`, `enrollments` | Student A seeing Student B's financial data |
| **High** | `student_progress`, `student_ratings`, `certificates`, `notifications` | Leaking academic records or private communications |
| **Medium** | `courses` (inactive), `modules`, `lessons`, `live_classes`, `recorded_classes` | Accessing premium content without enrollment |
| **System** | `audit_logs`, `system_settings` (private), `user_roles` | Privilege escalation, config exposure |

## How User Identity Reaches PostgreSQL

```
┌─────────────┐     JWT      ┌──────────────┐   SET LOCAL    ┌────────────┐
│   Client     │ ──────────> │   FastAPI     │ ────────────> │ PostgreSQL │
│              │             │  get_rls_db() │               │  RLS check │
└─────────────┘             └──────────────┘               └────────────┘
```

1. Client sends JWT in `Authorization: Bearer <token>`.
2. `get_current_user()` decodes the JWT → loads User from DB.
3. `get_rls_db()` dependency calls `SELECT set_config('app.current_user_id', '<uuid>', true)` and `SELECT set_config('app.current_user_role', '<role>', true)`.
4. All subsequent queries in the request use these values for RLS policy evaluation.
5. The `is_local=true` parameter makes the setting transaction-scoped — automatically discarded on `COMMIT` or `ROLLBACK`. The pooled connection is clean for the next request.

> **Note:** We use `set_config()` instead of `SET LOCAL` because PostgreSQL's extended query protocol (used by asyncpg) does not support parameter placeholders in `SET` commands. `set_config(name, value, is_local)` with `is_local=true` is functionally identical.

### Key Code: `backend/app/db/rls.py`

```python
from app.db.rls import get_rls_db, get_rls_db_optional, get_system_rls_db

# Authenticated endpoint → use get_rls_db
@router.get("/my-data")
async def get_data(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
): ...

# Public endpoint → use get_db (no RLS context)
@router.get("/catalog")
async def catalog(db: AsyncSession = Depends(get_db)): ...

# Optional auth → use get_rls_db_optional
@router.get("/mixed")
async def mixed(db: AsyncSession = Depends(get_rls_db_optional)): ...
```

## Database Role: `academy_app`

The application connects as `academy_app`, which has:
- ✅ `SELECT`, `INSERT`, `UPDATE`, `DELETE` on all tables
- ❌ No `SUPERUSER`
- ❌ No `BYPASSRLS`
- ❌ No `CREATEROLE`

> **CRITICAL**: If the app connects as `postgres` (superuser), RLS is completely bypassed. Always use `DATABASE_RLS_URL` in production.

## SQL Helper Functions

| Function | Returns | Used in policies as |
|----------|---------|-------------------|
| `app_user_id()` | `UUID` or `NULL` | `WHERE student_id = app_user_id()` |
| `app_user_role()` | `TEXT` (admin/teacher/student/user) | `WHERE app_user_role() = 'admin'` |
| `is_admin()` | `BOOLEAN` | `USING (is_admin() OR ...)` |

## How to Add RLS to a New Table

1. **Create the table** via migration as usual.

2. **Enable RLS** in a migration:
```sql
ALTER TABLE my_new_table ENABLE ROW LEVEL SECURITY;
ALTER TABLE my_new_table FORCE ROW LEVEL SECURITY;
```

3. **Create policies** for each operation:
```sql
-- SELECT: who can read?
CREATE POLICY my_table_select ON my_new_table FOR SELECT
    USING (owner_id = app_user_id() OR is_admin());

-- INSERT: who can create, and what constraints apply?
CREATE POLICY my_table_insert ON my_new_table FOR INSERT
    WITH CHECK (owner_id = app_user_id());

-- UPDATE: who can modify, and what can they change to?
CREATE POLICY my_table_update ON my_new_table FOR UPDATE
    USING (owner_id = app_user_id() OR is_admin())
    WITH CHECK (owner_id = app_user_id() OR is_admin());

-- DELETE: who can delete?
CREATE POLICY my_table_delete ON my_new_table FOR DELETE
    USING (is_admin());
```

4. **Grant permissions** to the app role:
```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON my_new_table TO academy_app;
```

5. **Use `get_rls_db`** in the endpoint that accesses this table.

6. **Write a test** in `tests/test_rls.py` to verify isolation.

## USING vs WITH CHECK — Quick Reference

| Clause | Applies to | Purpose | Default if omitted |
|--------|-----------|---------|-------------------|
| `USING` | SELECT, UPDATE (target rows), DELETE | "Can this user **see/touch** this row?" | Deny all |
| `WITH CHECK` | INSERT, UPDATE (new values) | "Can this user **create/change to** this row?" | Falls back to `USING` |

## Teacher-Scoped Writes: Contenido y Progreso (migración 024)

El docente escribe dos cosas que no están en `courses`: el temario
(`modules`/`lessons`) y el progreso de sus alumnos (`enrollments`). Ambas
escrituras las autorizan **dos capas** y hay que tocar las dos:

| Capa | Dónde | Qué decide |
|------|-------|-----------|
| Aplicación | `middlewares/rbac.py` → `ensure_course_manager`, `ensure_class_manager` | 404 si el recurso no existe, 403 si el docente no es el titular del curso/clase |
| Base de datos | `024_rls_teacher_curriculum_and_progress.sql` | `modules_delete`, `lessons_delete`, `enrollments_select` y `enrollments_update` incluyen al docente (del curso o de la clase) |

> **Pitfall**: si sólo se añade la comprobación en Python, en producción (RLS
> forzado) el `DELETE`/`UPDATE` afecta a **0 filas** y el endpoint responde 204 o
> 200 como si hubiera funcionado. Si sólo se añade la política, cualquier docente
> puede tocar cursos ajenos. Los tests de
> `tests/test_teacher_curriculum_progress.py` cubren el camino completo (app +
> RLS con el rol `academy_app`).

## Common Pitfalls

### 1. Superuser Bypasses RLS
Always connect with `academy_app`. Never use `postgres` for the running application.

### 2. Forgetting `FORCE ROW LEVEL SECURITY`
Without `FORCE`, the **table owner** bypasses RLS. Always include it.

### 3. JOINs Silently Drop Rows
If table A has RLS and table B doesn't, a JOIN may return fewer rows than expected. This is **by design** — RLS-filtered rows simply disappear from results.

### 4. Background Workers Need Context
The ARQ worker must set `SET LOCAL app.current_user_role = 'system'` using `get_system_rls_db()` to access tables like `email_queue` and `background_jobs`.

### 5. Auth Queries Run Before RLS Context
`get_current_user()` queries the `users` table before `SET LOCAL` is called. This is why `users` and `user_roles` have permissive SELECT policies (`USING (true)`). Write access is still restricted.

## Running RLS Tests

```bash
# From project root, with Docker containers running:
docker exec academy-backend pytest tests/test_rls.py -v

# Or locally with venv:
cd backend
RLS_TEST_DB_URL="postgresql+asyncpg://academy_app:academy_app_secure_pwd@localhost:5432/academy_db" \
    python -m pytest tests/test_rls.py -v
```

## Applying Migrations

For a **fresh database** (first `docker-compose up`):
- Migrations 009 and 010 run automatically via `docker-entrypoint-initdb.d`.

For an **existing database**:
```bash
# Connect to the postgres container
docker exec -i academy-postgres psql -U postgres -d academy_db < database/migrations/009_rls_role_and_functions.sql
docker exec -i academy-postgres psql -U postgres -d academy_db < database/migrations/010_rls_policies.sql
```

Las migraciones nuevas (024 en adelante) van por el servicio `migrate`, que las
aplica en orden y las registra en `schema_migrations` (aplicarlas a mano con
`psql` deja la tabla desincronizada y el runner intentará repetirlas):

```bash
cd docker && docker compose run --rm migrate
```

After applying, restart the backend to pick up the new `DATABASE_RLS_URL`.
