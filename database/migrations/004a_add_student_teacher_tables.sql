-- ============================================================================
-- CodeAcademy Pro — 004a: tablas students y teachers (faltaban en la cadena)
-- ============================================================================
-- Contexto del bug:
--   * app/models/user.py define los modelos Teacher (`teachers`) y Student
--     (`students`) desde el inicio, y el código los usa en todo el flujo
--     (inscripciones, asignación de profesores, panel de estudiante, seed).
--   * NINGUNA migración creaba esas dos tablas. La cadena nunca corrió sobre una
--     base vacía: la base local se generó con `Base.metadata.create_all()`, así
--     que las tablas existían y el hueco quedó invisible.
--   * Síntoma en una base nueva: 005_cleanup_user_data.sql muere con
--     `relation "students" does not exist` (y más adelante 010/011/013 fallarían
--     al crear políticas RLS y FKs sobre teachers).
--
-- Va ANTES de 005 a propósito (orden alfabético: 004_ < 004a_ < 005_), porque 005
-- borra filas de las dos y 011 modela la FK courses.teacher_id → teachers.id.
--
-- El DDL es el que produce el ORM (SQLAlchemy) para estos modelos.
-- ============================================================================

CREATE TABLE IF NOT EXISTS teachers (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE teachers IS 'Perfil de profesor: 1:1 con users (solo cambia el rol y los datos de negocio)';

CREATE TABLE IF NOT EXISTS students (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    enrollment_status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE students IS 'Perfil de estudiante: 1:1 con users';
