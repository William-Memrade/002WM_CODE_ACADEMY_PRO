# 🎓 CodeAcademy Pro

Academia virtual de programación con clases en vivo y pregrabadas.

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11+ / FastAPI |
| Frontend | Next.js 14+ (App Router) |
| Base de datos | Supabase PostgreSQL |
| Cache | Redis 7+ |
| Storage | Supabase Storage (S3-compatible) |
| Auth | JWT + bcrypt |
| Background Jobs | ARQ (async Redis queue) |
| Deploy | Docker + Docker Compose |

## Inicio Rápido

### 1. Clonar y configurar
```bash
git clone <repo>
cd Academy_Test
cp .env.example .env
# Editar .env con tus valores
```

### 2. Levantar con Docker
```bash
cd docker
docker compose up -d
```

### 3. Servicios disponibles
| Servicio | URL |
|----------|-----|
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |
| Frontend | http://localhost:3000 |
| Mailhog (email testing) | http://localhost:8025 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## Estructura del Proyecto

```
Academy_Test/
├── docs/architecture/    # Documentación técnica
├── database/migrations/  # Scripts SQL
├── backend/              # FastAPI API
│   ├── app/
│   │   ├── api/v1/       # Routers por dominio
│   │   ├── core/         # Config, security, observability
│   │   ├── db/           # Database session
│   │   ├── middlewares/  # Auth, RBAC, rate limiting
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── repositories/ # Data access layer
│   │   ├── schemas/      # Pydantic validation
│   │   ├── services/     # Business logic
│   │   └── utils/        # Validators, sanitizers
│   ├── tests/
│   └── main.py
├── frontend/             # Next.js 14+
├── docker/               # Docker Compose + Dockerfiles
├── .env.example
└── .gitignore
```

## Documentación

- [Arquitectura](docs/architecture/ARCHITECTURE.md)
- [Base de Datos](docs/architecture/DATABASE.md)
- [API Endpoints](docs/architecture/API_ENDPOINTS.md)
- [Seguridad](docs/architecture/SECURITY.md)
- [Flujos de Negocio](docs/architecture/FLOWS.md)
- [Paneles](docs/architecture/PANELS.md)
- [DevOps](docs/architecture/DEVOPS.md)
- [Pruebas y Calidad](docs/architecture/TESTING.md)
- [Roadmap](docs/architecture/ROADMAP.md)
- [Observabilidad](docs/architecture/OBSERVABILITY.md)
- [Background Jobs](docs/architecture/BACKGROUND_JOBS.md)
- [Emails](docs/architecture/EMAILS.md)
- [Feature Flags](docs/architecture/FEATURE_FLAGS.md)
- [Content Versioning](docs/architecture/CONTENT_VERSIONING.md)

## Licencia

Privado — Todos los derechos reservados.
