# 🐳 DevOps — CodeAcademy Pro

## Docker Compose (Development)

### Servicios
| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `backend` | 8000 | FastAPI + Uvicorn |
| `frontend` | 3000 | Next.js dev server |
| `postgres` | 5432 | PostgreSQL 16 (dev local) |
| `redis` | 6379 | Cache + job queue |
| `worker` | — | ARQ background worker |
| `mailhog` | 8025 | Email testing UI |

### Volúmenes
- `postgres_data` — persistencia BD
- `redis_data` — persistencia caché
- `./backend:/app` — hot reload backend
- `./frontend:/app` — hot reload frontend

---

## Estructura Docker

```
docker/
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx/
    └── nginx.conf
```

---

## CI/CD Recomendado

### Pipeline (GitHub Actions / GitLab CI)

```
1. Lint + Type Check (ruff, mypy, eslint)
2. Unit Tests (pytest, jest)
3. Build Docker images
4. Push to Container Registry
5. Deploy to Staging
6. Integration Tests
7. Deploy to Production (manual approval)
```

---

## Monitoring

### Stack recomendado
- **Métricas**: Prometheus + Grafana
- **Logs**: structlog → stdout → log aggregator (Loki/CloudWatch)
- **Alertas**: Grafana Alerting
- **Uptime**: Health check endpoints `/health` y `/health/ready`

### Dashboards Grafana sugeridos
1. API Performance (latencia, throughput, errors)
2. Business Metrics (pagos, inscripciones, usuarios activos)
3. Infrastructure (CPU, memoria, disco, conexiones DB)
4. Background Jobs (queue size, success/fail rate)

---

## Backups

| Dato | Frecuencia | Retención | Método |
|------|-----------|-----------|--------|
| PostgreSQL | Diario | 30 días | pg_dump / Supabase backup |
| Redis | No crítico | — | Redis RDB snapshots |
| Storage (S3) | — | Indefinida | Versionado S3 |

---

## Environments

| Env | Base de datos | Redis | Storage |
|-----|--------------|-------|---------|
| `development` | Docker local | Docker local | Local/MinIO |
| `staging` | Supabase (staging project) | Redis Cloud | Supabase Storage |
| `production` | Supabase (prod project) | Redis Cloud | Supabase Storage |

---

## Recomendaciones de Producción

1. **HTTPS obligatorio** — TLS termination en load balancer
2. **Variables de entorno** — Nunca en código, usar secrets manager
3. **Health checks** — Docker HEALTHCHECK + liveness/readiness probes
4. **Auto-scaling** — Min 2 instancias backend, scale por CPU/memory
5. **CDN** — Para assets estáticos del frontend
6. **WAF** — Web Application Firewall frente al load balancer
7. **Log rotation** — No llenar disco con logs
8. **Database connection pooling** — PgBouncer o Supabase pooler
9. **Redis persistence** — AOF para datos críticos, RDB para cache
10. **Secrets rotation** — JWT_SECRET, DB password rotación periódica
