-- ============================================================================
-- CodeAcademy Pro — FK Alignment: courses.teacher_id → teachers.id
--
-- PROBLEM:
--   001_initial_schema.sql defined: courses.teacher_id REFERENCES users(id)
--   ORM model defines:               ForeignKey("teachers.id")
--   RLS policies assume:             courses.teacher_id = teachers.id
--
--   If courses were created while the FK pointed to users(id), the column
--   stores users.id UUIDs — NOT teachers.id UUIDs. These are different PKs.
--
-- STRATEGY:
--   1. Detect which FK currently exists (users vs teachers vs none).
--   2. If FK → users: remap course.teacher_id values from users.id to
--      teachers.id using the teachers.user_id mapping.
--   3. Abort with clear error if any course has a teacher_id that cannot
--      be mapped (no teacher profile exists for that user).
--   4. Drop old FK, create new FK → teachers(id).
--   5. If FK → teachers already: skip (idempotent).
--
-- IDEMPOTENT: Safe to re-run. Detects current state before acting.
-- TRANSACTIONAL: Wrapped in BEGIN/COMMIT. On error, nothing is applied.
-- ============================================================================

BEGIN;

-- ── Step 1: Detect current state ────────────────────────────────────────────

DO $$
DECLARE
    fk_to_users TEXT;
    fk_to_teachers TEXT;
BEGIN
    -- Check for FK → users
    SELECT con.conname INTO fk_to_users
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_class frel ON frel.oid = con.confrelid
    WHERE rel.relname = 'courses'
      AND con.contype = 'f'
      AND con.conkey = ARRAY[(
          SELECT a.attnum FROM pg_attribute a
          WHERE a.attrelid = rel.oid AND a.attname = 'teacher_id'
      )]
      AND frel.relname = 'users';

    -- Check for FK → teachers
    SELECT con.conname INTO fk_to_teachers
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_class frel ON frel.oid = con.confrelid
    WHERE rel.relname = 'courses'
      AND con.contype = 'f'
      AND con.conkey = ARRAY[(
          SELECT a.attnum FROM pg_attribute a
          WHERE a.attrelid = rel.oid AND a.attname = 'teacher_id'
      )]
      AND frel.relname = 'teachers';

    IF fk_to_teachers IS NOT NULL THEN
        RAISE NOTICE '✅ FK courses.teacher_id → teachers(id) already exists (%). No changes needed.', fk_to_teachers;
        -- Nothing to do — skip all subsequent steps via a flag table.
        CREATE TEMP TABLE _migration_011_skip (skip BOOLEAN) ON COMMIT DROP;
        INSERT INTO _migration_011_skip VALUES (TRUE);
    ELSIF fk_to_users IS NOT NULL THEN
        RAISE NOTICE '⚠️  FK courses.teacher_id → users(id) found (%). Will remap data and replace FK.', fk_to_users;
        CREATE TEMP TABLE _migration_011_skip (skip BOOLEAN) ON COMMIT DROP;
        INSERT INTO _migration_011_skip VALUES (FALSE);
    ELSE
        RAISE NOTICE '⚠️  No FK found on courses.teacher_id. Will validate data and create FK → teachers(id).';
        CREATE TEMP TABLE _migration_011_skip (skip BOOLEAN) ON COMMIT DROP;
        INSERT INTO _migration_011_skip VALUES (FALSE);
    END IF;
END $$;

-- ── Step 2: Diagnose data (only if not skipping) ────────────────────────────

DO $$
DECLARE
    should_skip BOOLEAN;
    total_courses INTEGER;
    already_correct INTEGER;
    remappable INTEGER;
    orphaned INTEGER;
    orphan_row RECORD;
BEGIN
    SELECT skip INTO should_skip FROM _migration_011_skip LIMIT 1;
    IF should_skip THEN
        RETURN;
    END IF;

    -- Count total courses
    SELECT COUNT(*) INTO total_courses FROM courses;
    IF total_courses = 0 THEN
        RAISE NOTICE 'No courses in database. Skipping data transformation.';
        RETURN;
    END IF;

    -- Courses where teacher_id already matches a teachers.id (ORM-created)
    SELECT COUNT(*) INTO already_correct
    FROM courses c
    WHERE EXISTS (SELECT 1 FROM teachers t WHERE t.id = c.teacher_id);

    -- Courses where teacher_id is a users.id that has a teacher profile
    -- (can be remapped: users.id → teachers.id via teachers.user_id)
    SELECT COUNT(*) INTO remappable
    FROM courses c
    WHERE NOT EXISTS (SELECT 1 FROM teachers t WHERE t.id = c.teacher_id)
      AND EXISTS (SELECT 1 FROM teachers t WHERE t.user_id = c.teacher_id);

    -- Courses where teacher_id matches neither teachers.id nor any teachers.user_id
    -- (orphaned — no teacher profile exists for this user)
    SELECT COUNT(*) INTO orphaned
    FROM courses c
    WHERE NOT EXISTS (SELECT 1 FROM teachers t WHERE t.id = c.teacher_id)
      AND NOT EXISTS (SELECT 1 FROM teachers t WHERE t.user_id = c.teacher_id);

    RAISE NOTICE '── Data Diagnosis ──';
    RAISE NOTICE 'Total courses:     %', total_courses;
    RAISE NOTICE 'Already correct:   % (teacher_id matches teachers.id)', already_correct;
    RAISE NOTICE 'Remappable:        % (teacher_id matches users.id with teacher profile)', remappable;
    RAISE NOTICE 'Orphaned:          % (no teacher profile found)', orphaned;

    -- If there are orphaned rows, list them and ABORT
    IF orphaned > 0 THEN
        RAISE NOTICE '';
        RAISE NOTICE '❌ ORPHANED COURSES (no teacher profile for these user IDs):';
        FOR orphan_row IN
            SELECT c.id AS course_id, c.title, c.teacher_id,
                   u.email AS user_email
            FROM courses c
            LEFT JOIN users u ON u.id = c.teacher_id
            WHERE NOT EXISTS (SELECT 1 FROM teachers t WHERE t.id = c.teacher_id)
              AND NOT EXISTS (SELECT 1 FROM teachers t WHERE t.user_id = c.teacher_id)
        LOOP
            RAISE NOTICE '  course=% title=% teacher_id=% user_email=%',
                orphan_row.course_id, orphan_row.title,
                orphan_row.teacher_id, COALESCE(orphan_row.user_email, 'NOT FOUND IN USERS');
        END LOOP;
        RAISE NOTICE '';
        RAISE NOTICE 'Fix: Create teacher profiles for these users first:';
        RAISE NOTICE '  INSERT INTO teachers (id, user_id, is_active) VALUES (gen_random_uuid(), ''<user_id>'', true);';
        RAISE NOTICE 'Then re-run this migration.';
        RAISE EXCEPTION 'Migration aborted: % course(s) have teacher_id values with no corresponding teacher profile. See NOTICE messages above.', orphaned;
    END IF;
END $$;

-- ── Step 3: Remap data (only if not skipping) ───────────────────────────────

DO $$
DECLARE
    should_skip BOOLEAN;
    remapped INTEGER;
BEGIN
    SELECT skip INTO should_skip FROM _migration_011_skip LIMIT 1;
    IF should_skip THEN
        RETURN;
    END IF;

    -- Remap: courses.teacher_id = users.id → teachers.id
    -- Only update rows where teacher_id is NOT already a teachers.id
    UPDATE courses c
    SET teacher_id = t.id
    FROM teachers t
    WHERE t.user_id = c.teacher_id                                      -- match user → teacher profile
      AND NOT EXISTS (SELECT 1 FROM teachers t2 WHERE t2.id = c.teacher_id);  -- skip if already correct

    GET DIAGNOSTICS remapped = ROW_COUNT;

    IF remapped > 0 THEN
        RAISE NOTICE '✅ Remapped % course(s): teacher_id changed from users.id to teachers.id', remapped;
    ELSE
        RAISE NOTICE 'No courses needed remapping (all already use teachers.id)';
    END IF;

    -- Verify all courses now point to valid teachers.id
    IF EXISTS (
        SELECT 1 FROM courses c
        WHERE NOT EXISTS (SELECT 1 FROM teachers t WHERE t.id = c.teacher_id)
    ) THEN
        RAISE EXCEPTION 'Post-remap validation failed: some courses still have invalid teacher_id values';
    END IF;

    RAISE NOTICE '✅ Post-remap validation passed: all courses.teacher_id reference a valid teachers.id';
END $$;

-- ── Step 4: Drop old FK (only if not skipping) ─────────────────────────────

DO $$
DECLARE
    should_skip BOOLEAN;
    fk_name TEXT;
BEGIN
    SELECT skip INTO should_skip FROM _migration_011_skip LIMIT 1;
    IF should_skip THEN
        RETURN;
    END IF;

    -- Find and drop any FK on teacher_id that points to users
    SELECT con.conname INTO fk_name
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_class frel ON frel.oid = con.confrelid
    WHERE rel.relname = 'courses'
      AND con.contype = 'f'
      AND con.conkey = ARRAY[(
          SELECT a.attnum FROM pg_attribute a
          WHERE a.attrelid = rel.oid AND a.attname = 'teacher_id'
      )]
      AND frel.relname = 'users';

    IF fk_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE courses DROP CONSTRAINT %I', fk_name);
        RAISE NOTICE '✅ Dropped FK constraint: % (courses.teacher_id → users.id)', fk_name;
    ELSE
        RAISE NOTICE 'No FK → users(id) to drop (may have been created without explicit FK or already dropped)';
    END IF;
END $$;

-- ── Step 5: Create new FK (only if not skipping) ────────────────────────────

DO $$
DECLARE
    should_skip BOOLEAN;
    fk_exists BOOLEAN;
BEGIN
    SELECT skip INTO should_skip FROM _migration_011_skip LIMIT 1;
    IF should_skip THEN
        RETURN;
    END IF;

    -- Check if FK → teachers already exists (shouldn't at this point, but be safe)
    SELECT EXISTS(
        SELECT 1 FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_class frel ON frel.oid = con.confrelid
        WHERE rel.relname = 'courses'
          AND con.contype = 'f'
          AND con.conkey = ARRAY[(
              SELECT a.attnum FROM pg_attribute a
              WHERE a.attrelid = rel.oid AND a.attname = 'teacher_id'
          )]
          AND frel.relname = 'teachers'
    ) INTO fk_exists;

    IF NOT fk_exists THEN
        ALTER TABLE courses
            ADD CONSTRAINT fk_courses_teacher_id
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT;
        RAISE NOTICE '✅ Created FK: courses.teacher_id → teachers(id) ON DELETE RESTRICT';
    ELSE
        RAISE NOTICE 'FK courses.teacher_id → teachers(id) already exists';
    END IF;
END $$;

-- ── Step 6: Final verification ──────────────────────────────────────────────

DO $$
DECLARE
    r RECORD;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '── Final State ──';
    FOR r IN
        SELECT con.conname, frel.relname AS references_table
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_class frel ON frel.oid = con.confrelid
        WHERE rel.relname = 'courses'
          AND con.contype = 'f'
          AND con.conkey = ARRAY[(
              SELECT a.attnum FROM pg_attribute a
              WHERE a.attrelid = rel.oid AND a.attname = 'teacher_id'
          )]
    LOOP
        RAISE NOTICE '  courses.teacher_id FK → % (constraint: %)', r.references_table, r.conname;
    END LOOP;
END $$;

COMMIT;
