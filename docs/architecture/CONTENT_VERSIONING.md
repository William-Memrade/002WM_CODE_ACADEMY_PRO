# 📜 Content Versioning — CodeAcademy Pro

## Diseño

Cada update a un curso, módulo o lección guarda automáticamente un snapshot JSONB del estado anterior.

## Tabla `content_versions`
- `entity_type`: course, module, lesson
- `entity_id`: UUID de la entidad
- `version_number`: auto-incremental por entidad
- `snapshot`: JSONB con estado completo
- `changed_by`: usuario que hizo el cambio
- `change_summary`: descripción opcional

## Flujo
1. Docente edita un curso/módulo/lección
2. Service layer guarda snapshot del estado actual ANTES del update
3. Se incrementa version_number
4. Se aplica el update

## Acceso
- **Docente**: Ve historial de cambios de SUS cursos
- **Admin**: Ve todo el historial, puede restaurar versiones

## Retención
- Últimas 50 versiones por entidad (configurable en `system_settings`)
- Background job limpia versiones antiguas diariamente

## Restauración
- Solo admin puede restaurar
- Restaurar = crear nueva versión con contenido de la versión antigua
- Audit log: `content_restored`
