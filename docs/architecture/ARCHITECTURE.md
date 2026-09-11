# 🏗️ Arquitectura General — CodeAcademy Pro

## Visión General

CodeAcademy Pro es una plataforma LMS de academia virtual de programación diseñada como un **monolito modular** con separación clara de dominios, preparada para evolucionar hacia microservicios cuando el volumen lo requiera.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTES                                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐                   │
│   │ Browser  │   │Mobile App│   │  API     │                    │
│   │(Next.js) │   │ (futuro) │   │Consumers │                   │
│   └────┬─────┘   └────┬─────┘   └────┬─────┘                   │
└────────┼──────────────┼──────────────┼──────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOAD BALANCER / REVERSE PROXY                 │
│                         (Nginx / Traefik)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   FRONTEND     │  │    BACKEND     │  │   STATIC       │
│   Next.js 14+  │  │    FastAPI     │  │   ASSETS       │
│   App Router   │  │    Uvicorn     │  │   CDN/S3       │
│   Port: 3000   │  │    Port: 8000  │  │                │
└────────────────┘  └───────┬────────┘  └────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────────┐
     │  PostgreSQL  │ │  Redis   │ │ S3 Storage   │
     │  (Supabase)  │ │  Cache + │ │ (Supabase    │
     │              │ │  Queue   │ │  Storage)    │
     └──────────────┘ └──────────┘ └──────────────┘
```

---

## Stack Tecnológico

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| **Backend** | Python 3.11+ / FastAPI | Async nativo, tipado fuerte, OpenAPI automático |
| **Frontend** | Next.js 14+ (App Router) | SSR/SSG, React Server Components, SEO |
| **Base de datos** | Supabase PostgreSQL | Managed, escalable, con Storage integrado |
| **Cache** | Redis 7+ | Sesiones, rate limiting, feature flags, job queue |
| **Storage** | Supabase Storage (S3-compatible) | Archivos, comprobantes de pago, videos |
| **Auth** | JWT (python-jose) + bcrypt (passlib) | Control total, sin vendor lock-in |
| **ORM** | SQLAlchemy 2.0 (async) | Type-safe, migraciones con Alembic |
| **Validación** | Pydantic v2 | Schemas estrictos, serialización rápida |
| **Background Jobs** | ARQ (async Redis queue) | Lightweight, Python async nativo |
| **Email** | SMTP + Jinja2 templates | Provider-agnostic (SendGrid/SES/Resend) |
| **Observabilidad** | structlog + Prometheus | Logs JSON, métricas, health checks |
| **Deploy** | Docker + Docker Compose | Reproducible, cloud-ready |

---

## Patrones de Diseño

### 1. Arquitectura en Capas (Layered Architecture)

```
┌─────────────────────────────────┐
│         API Layer               │  ← Routers FastAPI (controllers)
│         (app/api/v1/)           │
├─────────────────────────────────┤
│         Service Layer           │  ← Lógica de negocio
│         (app/services/)         │
├─────────────────────────────────┤
│         Repository Layer        │  ← Acceso a datos (SQLAlchemy)
│         (app/repositories/)     │
├─────────────────────────────────┤
│         Model Layer             │  ← Modelos ORM + Schemas Pydantic
│         (app/models/ + schemas/)│
├─────────────────────────────────┤
│         Infrastructure          │  ← DB, Redis, Storage, Email
│         (app/core/ + db/)       │
└─────────────────────────────────┘
```

**Reglas de dependencia:**
- API → Service → Repository → Model
- Nunca saltar capas (API no accede directamente a Repository)
- Services pueden llamar a otros Services
- Repositories solo acceden a la base de datos

### 2. Repository Pattern

Abstrae el acceso a datos del resto de la aplicación:

```python
# app/repositories/course_repository.py
class CourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, course_id: UUID) -> Course | None: ...
    async def get_active(self, skip: int, limit: int) -> list[Course]: ...
    async def create(self, data: CourseCreate) -> Course: ...
    async def update(self, course_id: UUID, data: CourseUpdate) -> Course: ...
    async def soft_delete(self, course_id: UUID) -> None: ...
```

### 3. Service Layer

Encapsula la lógica de negocio, orquesta repositories y servicios externos:

```python
# app/services/enrollment_service.py
class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.enrollment_repo = EnrollmentRepository(db)
        self.course_repo = CourseRepository(db)
        self.notification_service = NotificationService(db)

    async def enroll(self, student_id: UUID, course_id: UUID) -> Enrollment:
        # Validar curso activo
        # Verificar no duplicado
        # Crear enrollment con estado pending_payment
        # Notificar al alumno
        ...
```

### 4. Dependency Injection (FastAPI native)

```python
# app/api/deps.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    ...
```

---

## Estrategia de Caché (Redis)

### Capas de Caché

| Dato | TTL | Estrategia | Invalidación |
|------|-----|-----------|-------------|
| Feature flags | 60s | Read-through | On update via API |
| Catálogo de cursos activos | 300s | Cache-aside | On course create/update/delete |
| Detalle de curso | 600s | Cache-aside | On course update |
| Métricas dashboard admin | 120s | Cache-aside | On scheduled recalc |
| Sesión usuario (refresh token) | 7 días | Direct | On logout/token refresh |
| Rate limit counters | 60s | Direct | Auto-expire |

### Patrón Cache-Aside

```python
async def get_course(course_id: UUID) -> Course:
    # 1. Buscar en Redis
    cached = await redis.get(f"course:{course_id}")
    if cached:
        return Course.model_validate_json(cached)

    # 2. Buscar en DB
    course = await course_repo.get_by_id(course_id)

    # 3. Guardar en Redis
    await redis.set(f"course:{course_id}", course.model_dump_json(), ex=600)
    return course
```

---

## Estrategia de Storage (S3-Compatible)

### Estructura de Buckets

```
academy-storage/
├── payment-proofs/          # Comprobantes de pago
│   └── {enrollment_id}/
│       └── {timestamp}_{filename}
├── recorded-classes/        # Videos pregrabados
│   └── {course_id}/
│       └── {lesson_id}/
│           └── {filename}
├── certificates/            # Certificados PDF generados
│   └── {student_id}/
│       └── {certificate_id}.pdf
├── avatars/                 # Fotos de perfil
│   └── {user_id}/
│       └── avatar.{ext}
└── course-thumbnails/       # Thumbnails de cursos
    └── {course_id}/
        └── thumbnail.{ext}
```

### Seguridad de Storage
- URLs pre-firmadas (signed URLs) con expiración para acceso temporal
- Validación de MIME type real (no solo extensión)
- Límite de tamaño por tipo de archivo
- Archivos de pago: solo accesibles por admin y el alumno dueño
- Videos: solo accesibles por alumnos con inscripción aprobada

---

## Comunicación entre Componentes

### Actual (Monolito Modular)

```
Frontend ─── HTTP/REST ───► Backend API
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                  Service   Service   Service
                    │         │         │
                    ▼         ▼         ▼
                  Repository (todos comparten misma DB)
```

### Futuro (Microservicios)

```
API Gateway ──► Auth Service ──► User DB
            ├─► Course Service ──► Course DB
            ├─► Payment Service ──► Payment DB
            ├─► Notification Service ──► Redis + Email
            └─► Analytics Service ──► Analytics DB

Comunicación interna: HMAC-signed HTTP / Event Bus (Redis Streams)
```

La transición es posible porque cada servicio ya está aislado en su propio módulo con su propia interfaz.

---

## Escalabilidad Horizontal

### Fase 1: Monolito (0-10K usuarios)
- 1 instancia Backend + 1 Worker
- Supabase managed PostgreSQL
- Redis single instance
- Docker Compose

### Fase 2: Escalado (10K-100K usuarios)
- N instancias Backend detrás de Load Balancer
- N Workers ARQ
- PostgreSQL con read replicas
- Redis Cluster
- CDN para assets estáticos
- Docker Compose → Kubernetes

### Fase 3: Microservicios (100K+ usuarios)
- Servicios independientes por dominio
- Event-driven architecture (Redis Streams → Kafka)
- Base de datos por servicio
- API Gateway
- Service Mesh

---

## Estructura de Proyecto

```
Academy_Test/
├── docs/
│   └── architecture/          # Documentación técnica
├── database/
│   └── migrations/            # Scripts SQL
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/            # Versioned API routers
│   │   │       ├── auth/
│   │   │       ├── courses/
│   │   │       ├── payments/
│   │   │       ├── users/
│   │   │       ├── reviews/
│   │   │       ├── notifications/
│   │   │       └── audit/
│   │   ├── core/              # Config, security, observability
│   │   ├── db/                # Database session, engine
│   │   ├── middlewares/       # Auth, RBAC, rate limiting
│   │   ├── models/            # SQLAlchemy models
│   │   ├── repositories/     # Data access layer
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic + external services
│   │   └── utils/             # Validators, sanitizers, audit
│   ├── tests/
│   ├── scripts/               # CLI scripts, seeders
│   ├── main.py
│   └── requirements.txt
├── frontend/                  # Next.js 14+ App Router
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   │   ├── (public)/      # Páginas públicas (landing, cursos)
│   │   │   ├── (auth)/        # Login, Register
│   │   │   ├── admin/         # Panel Admin
│   │   │   ├── teacher/       # Panel Docente
│   │   │   └── student/       # Panel Alumno
│   │   ├── components/        # Componentes reutilizables
│   │   ├── lib/               # Utilidades, API client
│   │   ├── hooks/             # Custom hooks
│   │   └── styles/            # CSS global
│   └── public/
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── .env.example
├── .gitignore
└── README.md
```
