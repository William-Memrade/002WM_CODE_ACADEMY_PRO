-- Migración para hacer nullable el campo teacher_id en la tabla courses
-- Asegura que esta migración es segura de reejecutar

ALTER TABLE courses ALTER COLUMN teacher_id DROP NOT NULL;