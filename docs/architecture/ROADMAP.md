# 🗺️ Roadmap de Desarrollo — CodeAcademy Pro

## Fase 1: MVP Core (Sprints 1-4) — ~8 semanas

### Sprint 1: Fundación
- [x] Arquitectura documentada
- [ ] Proyecto backend (FastAPI scaffold)
- [ ] Base de datos: schema + migraciones
- [ ] Auth: registro, login, JWT, refresh
- [ ] RBAC básico (admin, teacher, student)
- [ ] Docker Compose dev environment

### Sprint 2: Cursos + Inscripciones
- [ ] CRUD cursos (admin)
- [ ] Categorías
- [ ] Módulos y lecciones
- [ ] Catálogo público de cursos
- [ ] Inscripción de alumnos
- [ ] Asignación docentes a cursos

### Sprint 3: Pagos + Contenido
- [ ] Flujo de pago manual completo
- [ ] Upload de comprobantes
- [ ] Aprobación/rechazo por admin
- [ ] Clases grabadas (upload + streaming)
- [ ] Clases en vivo (links)
- [ ] Progreso del alumno

### Sprint 4: Frontend MVP
- [ ] Proyecto Next.js scaffold
- [ ] Landing page
- [ ] Catálogo de cursos
- [ ] Auth pages (login, register)
- [ ] Panel alumno (dashboard, cursos, pagos)
- [ ] Panel admin (dashboard, pagos, cursos)
- [ ] Panel docente (dashboard, temario)

---

## Fase 2: Features Completas (Sprints 5-7) — ~6 semanas

### Sprint 5: Comunicación + Feedback
- [ ] Notificaciones in-app
- [ ] Sistema de emails transaccionales
- [ ] Reseñas de cursos
- [ ] Sugerencias
- [ ] Certificados (emisión + PDF)

### Sprint 6: Reputación + Observabilidad
- [ ] Calificación de alumnos (docente)
- [ ] Sistema de estrellas
- [ ] Alumnos destacados
- [ ] Alumnos listos evaluación externa
- [ ] Logging estructurado
- [ ] Health checks
- [ ] Métricas Prometheus

### Sprint 7: Admin Avanzado
- [ ] Auditoría completa
- [ ] Feature flags
- [ ] Content versioning
- [ ] Background jobs (ARQ)
- [ ] Rate limiting
- [ ] System settings

---

## Fase 3: Pulido + Producción (Sprints 8-9) — ~4 semanas

### Sprint 8: Testing + Security
- [ ] Tests unitarios (>80% coverage backend)
- [ ] Tests de integración API
- [ ] Tests E2E frontend (Playwright)
- [ ] Security audit (OWASP checklist)
- [ ] Performance testing (k6/locust)
- [ ] Fix de bugs

### Sprint 9: Deploy + Launch
- [ ] Docker producción optimizado
- [ ] CI/CD pipeline
- [ ] Monitoring (Grafana dashboards)
- [ ] Documentación de deploy
- [ ] Seed data de producción
- [ ] Launch preparation

---

## Fase 4: Evolución (Post-Launch)

### V2 — Mejoras
- [ ] Pasarela de pago online (Stripe/PayPal)
- [ ] Sistema de cupones/descuentos
- [ ] Búsqueda full-text (PostgreSQL ts_vector)
- [ ] Internacionalización (i18n)
- [ ] PWA support
- [ ] Dark mode

### V3 — Expansión
- [ ] App móvil (React Native)
- [ ] IA Tutor (chatbot con RAG)
- [ ] Analytics avanzado (dashboards custom)
- [ ] Bolsa de empleo
- [ ] Integración empresas (B2B)
- [ ] API pública para partners

### V4 — Escala
- [ ] Migración a microservicios
- [ ] Event-driven architecture
- [ ] Kubernetes deployment
- [ ] Multi-tenancy
- [ ] CDN para video streaming
- [ ] Real-time features (WebSocket)
