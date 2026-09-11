-- ============================================================================
-- CodeAcademy Pro — Database Cleanup
-- Removes ALL non-admin user data while preserving courses, categories,
-- modules, lessons, system settings, feature flags, roles, and teachers
-- that are assigned to courses.
-- Run this ONCE to reset the platform for real user testing.
-- ============================================================================

BEGIN;

-- 1. Remove payment proofs
DELETE FROM payment_proofs;

-- 2. Remove payments
DELETE FROM payments;

-- 3. Remove enrollments
DELETE FROM enrollments;

-- 4. Remove optional tables (may not exist in all environments)
DO $$ BEGIN
  EXECUTE 'DELETE FROM notifications' || '';
EXCEPTION WHEN undefined_table THEN NULL;
END $$;

DO $$ BEGIN
  EXECUTE 'DELETE FROM student_highlights' || '';
EXCEPTION WHEN undefined_table THEN NULL;
END $$;

DO $$ BEGIN
  EXECUTE 'DELETE FROM reviews' || '';
EXCEPTION WHEN undefined_table THEN NULL;
END $$;

DO $$ BEGIN
  EXECUTE 'DELETE FROM certificates' || '';
EXCEPTION WHEN undefined_table THEN NULL;
END $$;

-- 5. Remove student profiles
DELETE FROM students;

-- 6. Identify users to keep:
--    - Admin users (have admin role)
--    - Users who own teacher profiles that are assigned to active courses
CREATE TEMP TABLE _keep_user_ids AS
  -- admin users
  SELECT ur.user_id FROM user_roles ur
  JOIN roles r ON r.id = ur.role_id
  WHERE r.name = 'admin'
  UNION
  -- teacher users assigned to courses
  SELECT t.user_id FROM teachers t
  WHERE t.id IN (SELECT DISTINCT teacher_id FROM courses WHERE deleted_at IS NULL);

-- 7. Remove user_roles for users NOT in the keep list
DELETE FROM user_roles
WHERE user_id NOT IN (SELECT user_id FROM _keep_user_ids);

-- 8. Remove teachers NOT assigned to courses and NOT admin
DELETE FROM teachers
WHERE user_id NOT IN (SELECT user_id FROM _keep_user_ids);

-- 9. Remove users NOT in the keep list
DELETE FROM users
WHERE id NOT IN (SELECT user_id FROM _keep_user_ids);

-- 10. Drop temp table
DROP TABLE _keep_user_ids;

COMMIT;

-- Verify the cleanup
SELECT 'Remaining users:' AS info, COUNT(*) AS count FROM users
UNION ALL
SELECT 'Remaining courses:', COUNT(*) FROM courses WHERE deleted_at IS NULL
UNION ALL
SELECT 'Remaining categories:', COUNT(*) FROM categories
UNION ALL
SELECT 'Remaining enrollments:', COUNT(*) FROM enrollments
UNION ALL
SELECT 'Remaining payments:', COUNT(*) FROM payments
UNION ALL
SELECT 'Remaining students:', COUNT(*) FROM students
UNION ALL
SELECT 'Remaining teachers:', COUNT(*) FROM teachers;
