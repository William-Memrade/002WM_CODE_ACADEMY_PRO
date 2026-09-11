"""
CodeAcademy Pro — Seed Script
Creates default admin, teacher users and 6 courses with unique syllabi.
Run: cd backend && source venv/bin/activate && python scripts/seed_data.py
"""

import asyncio
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.session import async_session
from app.core.security import hash_password
from app.models.user import User, Role, UserRole, Teacher, Student
from app.models.course import Course, Module, Lesson, Category


# ── COURSES & SYLLABI ────────────────────────────────────────────────────────

COURSES_DATA = [
    {
        "title": "Python desde Cero",
        "slug": "python-desde-cero",
        "description": "Aprende Python desde los fundamentos hasta desarrollo profesional. Cubre sintaxis, estructuras de datos, POO, manejo de archivos, APIs y proyectos reales.",
        "short_description": "Domina Python desde cero hasta nivel profesional con proyectos reales.",
        "level": "beginner",
        "price": 49.99,
        "duration_hours": 60,
        "max_students": 100,
        "is_active": True,
        "is_featured": True,
        "category_slug": "python",
        "modules": [
            {"title": "Introducción a Python", "lessons": [
                {"title": "¿Qué es Python y por qué aprenderlo?", "duration": 15, "is_free": True},
                {"title": "Instalación del entorno (Python + VS Code)", "duration": 20, "is_free": True},
                {"title": "Tu primer programa: Hola Mundo", "duration": 10, "is_free": True},
                {"title": "El intérprete interactivo y scripts .py", "duration": 15},
            ]},
            {"title": "Variables y Tipos de Datos", "lessons": [
                {"title": "Variables y asignación", "duration": 20},
                {"title": "Strings: métodos y f-strings", "duration": 25},
                {"title": "Números: int, float y operaciones", "duration": 20},
                {"title": "Booleanos y conversiones de tipo", "duration": 15},
            ]},
            {"title": "Control de Flujo", "lessons": [
                {"title": "Condicionales: if, elif, else", "duration": 25},
                {"title": "Bucles: for y range()", "duration": 25},
                {"title": "Bucles: while y control (break, continue)", "duration": 20},
                {"title": "Comprensiones de lista", "duration": 20},
            ]},
            {"title": "Estructuras de Datos", "lessons": [
                {"title": "Listas: crear, modificar, iterar", "duration": 30},
                {"title": "Tuplas y conjuntos", "duration": 20},
                {"title": "Diccionarios a fondo", "duration": 30},
                {"title": "Proyecto: Agenda de contactos", "duration": 45},
            ]},
            {"title": "Funciones y Módulos", "lessons": [
                {"title": "Definir y llamar funciones", "duration": 25},
                {"title": "Parámetros, args y kwargs", "duration": 20},
                {"title": "Funciones lambda y map/filter", "duration": 20},
                {"title": "Módulos y paquetes (import)", "duration": 20},
            ]},
            {"title": "POO en Python", "lessons": [
                {"title": "Clases y objetos", "duration": 30},
                {"title": "Herencia y polimorfismo", "duration": 25},
                {"title": "Métodos mágicos (__str__, __init__)", "duration": 20},
                {"title": "Proyecto: Sistema de inventario POO", "duration": 45},
            ]},
            {"title": "Manejo de Archivos y Errores", "lessons": [
                {"title": "Leer y escribir archivos (txt, csv)", "duration": 25},
                {"title": "Manejo de JSON", "duration": 20},
                {"title": "Try/except y excepciones personalizadas", "duration": 25},
                {"title": "Context managers (with)", "duration": 15},
            ]},
            {"title": "Proyecto Final: API REST con Flask", "lessons": [
                {"title": "Introducción a Flask", "duration": 25},
                {"title": "Rutas, templates y formularios", "duration": 30},
                {"title": "Conexión a base de datos SQLite", "duration": 30},
                {"title": "Deploy del proyecto en Railway", "duration": 25},
            ]},
        ],
    },
    {
        "title": "React Avanzado",
        "slug": "react-avanzado",
        "description": "Lleva tus habilidades de React al siguiente nivel. Hooks avanzados, Context API, patrones de diseño, performance, testing y arquitectura en aplicaciones profesionales.",
        "short_description": "Hooks avanzados, patrones, performance y testing para React profesional.",
        "level": "advanced",
        "price": 79.99,
        "duration_hours": 50,
        "max_students": 80,
        "is_active": True,
        "is_featured": True,
        "category_slug": "frontend",
        "modules": [
            {"title": "Hooks Avanzados", "lessons": [
                {"title": "useReducer para estado complejo", "duration": 25, "is_free": True},
                {"title": "useCallback y useMemo: cuándo y por qué", "duration": 30},
                {"title": "useRef: más allá del DOM", "duration": 20},
                {"title": "Custom Hooks: patrones reutilizables", "duration": 35},
            ]},
            {"title": "Gestión de Estado Global", "lessons": [
                {"title": "Context API + useReducer vs Redux", "duration": 30},
                {"title": "Zustand: estado global simple", "duration": 25},
                {"title": "React Query: server state", "duration": 35},
                {"title": "Patrón: estado local vs global vs server", "duration": 20},
            ]},
            {"title": "Patrones de Diseño en React", "lessons": [
                {"title": "Compound Components", "duration": 30},
                {"title": "Render Props y HOC", "duration": 25},
                {"title": "Controlled vs Uncontrolled", "duration": 20},
                {"title": "Provider Pattern y Dependency Injection", "duration": 25},
            ]},
            {"title": "Performance y Optimización", "lessons": [
                {"title": "React DevTools Profiler", "duration": 20},
                {"title": "React.memo, lazy y Suspense", "duration": 30},
                {"title": "Virtualización de listas (react-window)", "duration": 25},
                {"title": "Code splitting y bundle analysis", "duration": 25},
            ]},
            {"title": "Testing en React", "lessons": [
                {"title": "Jest + React Testing Library setup", "duration": 20},
                {"title": "Testing de componentes y hooks", "duration": 30},
                {"title": "Mocking de APIs y módulos", "duration": 25},
                {"title": "Integration tests y coverage", "duration": 25},
            ]},
            {"title": "Proyecto: Dashboard SaaS", "lessons": [
                {"title": "Arquitectura y setup del proyecto", "duration": 30},
                {"title": "Autenticación con JWT y rutas protegidas", "duration": 35},
                {"title": "Gráficas con Recharts y tablas editables", "duration": 30},
                {"title": "Deploy en Vercel con CI/CD", "duration": 25},
            ]},
        ],
    },
    {
        "title": "Node.js y Express",
        "slug": "nodejs-express",
        "description": "Construye APIs RESTful profesionales con Node.js y Express. Middleware, autenticación JWT, bases de datos, WebSockets y despliegue en producción.",
        "short_description": "APIs RESTful con Node.js, Express, JWT, databases y deploy.",
        "level": "intermediate",
        "price": 59.99,
        "duration_hours": 48,
        "max_students": 90,
        "is_active": True,
        "is_featured": False,
        "category_slug": "backend",
        "modules": [
            {"title": "Fundamentos de Node.js", "lessons": [
                {"title": "Node.js: event loop y arquitectura", "duration": 20, "is_free": True},
                {"title": "Módulos CommonJS y ESM", "duration": 15},
                {"title": "npm, package.json y scripts", "duration": 20},
                {"title": "Async/Await y Promises", "duration": 25},
            ]},
            {"title": "Express Framework", "lessons": [
                {"title": "Setup de Express y primer servidor", "duration": 20},
                {"title": "Rutas, params y query strings", "duration": 25},
                {"title": "Middleware: concepto y stack", "duration": 25},
                {"title": "Manejo de errores centralizado", "duration": 20},
            ]},
            {"title": "Bases de Datos", "lessons": [
                {"title": "PostgreSQL con pg y pool", "duration": 30},
                {"title": "MongoDB con Mongoose", "duration": 25},
                {"title": "Prisma ORM: schema, migrations, queries", "duration": 30},
            ]},
            {"title": "Autenticación y Seguridad", "lessons": [
                {"title": "JWT: access y refresh tokens", "duration": 30},
                {"title": "bcrypt, helmet, cors", "duration": 20},
                {"title": "Rate limiting y protección XSS", "duration": 20},
                {"title": "RBAC: roles y permisos", "duration": 25},
            ]},
            {"title": "Funcionalidades Avanzadas", "lessons": [
                {"title": "Subida de archivos con Multer", "duration": 25},
                {"title": "WebSockets con Socket.io", "duration": 30},
                {"title": "Background jobs con Bull/BullMQ", "duration": 25},
                {"title": "Envío de emails con Nodemailer", "duration": 20},
            ]},
            {"title": "Proyecto Final: API E-Commerce", "lessons": [
                {"title": "Diseño de la API y modelos", "duration": 25},
                {"title": "CRUD de productos y carrito", "duration": 35},
                {"title": "Pasarela de pagos (Stripe)", "duration": 30},
                {"title": "Docker + deploy en Railway", "duration": 25},
            ]},
        ],
    },
    {
        "title": "SQL y PostgreSQL",
        "slug": "sql-postgresql",
        "description": "Domina SQL desde consultas básicas hasta optimización avanzada. Modelado, joins, subqueries, funciones de ventana, índices, procedimientos y administración de PostgreSQL.",
        "short_description": "SQL completo: desde SELECT hasta optimización y administración de PostgreSQL.",
        "level": "beginner",
        "price": 39.99,
        "duration_hours": 40,
        "max_students": 120,
        "is_active": True,
        "is_featured": False,
        "category_slug": "databases",
        "modules": [
            {"title": "Fundamentos SQL", "lessons": [
                {"title": "¿Qué es SQL y bases de datos relacionales?", "duration": 15, "is_free": True},
                {"title": "Instalar PostgreSQL y pgAdmin", "duration": 20, "is_free": True},
                {"title": "SELECT, FROM, WHERE", "duration": 20},
                {"title": "ORDER BY, LIMIT, DISTINCT", "duration": 15},
            ]},
            {"title": "Manipulación de Datos", "lessons": [
                {"title": "INSERT, UPDATE, DELETE", "duration": 20},
                {"title": "Tipos de datos en PostgreSQL", "duration": 20},
                {"title": "Constraints: PK, FK, UNIQUE, CHECK", "duration": 25},
                {"title": "ALTER TABLE y migraciones", "duration": 20},
            ]},
            {"title": "Consultas Avanzadas", "lessons": [
                {"title": "JOINs: INNER, LEFT, RIGHT, FULL", "duration": 30},
                {"title": "Subqueries y CTEs (WITH)", "duration": 30},
                {"title": "Funciones de agregación y GROUP BY", "duration": 25},
                {"title": "HAVING y filtros avanzados", "duration": 15},
            ]},
            {"title": "Funciones de Ventana y Avanzadas", "lessons": [
                {"title": "ROW_NUMBER, RANK, DENSE_RANK", "duration": 25},
                {"title": "LAG, LEAD, FIRST_VALUE", "duration": 25},
                {"title": "Particiones y frames", "duration": 20},
                {"title": "CASE WHEN, COALESCE, NULLIF", "duration": 20},
            ]},
            {"title": "Administración y Optimización", "lessons": [
                {"title": "Índices: B-tree, GIN, hash", "duration": 30},
                {"title": "EXPLAIN ANALYZE y plan de ejecución", "duration": 30},
                {"title": "Vistas, vistas materializadas", "duration": 20},
                {"title": "Backups, restore y seguridad", "duration": 25},
            ]},
        ],
    },
    {
        "title": "Docker y DevOps",
        "slug": "docker-devops",
        "description": "Aprende a contenerizar aplicaciones con Docker y a implementar CI/CD. Docker Compose, registries, GitHub Actions, monitoreo y orquestación básica.",
        "short_description": "Containers, Docker Compose, CI/CD y despliegue profesional.",
        "level": "intermediate",
        "price": 69.99,
        "duration_hours": 45,
        "max_students": 80,
        "is_active": True,
        "is_featured": True,
        "category_slug": "devops",
        "modules": [
            {"title": "Fundamentos de Docker", "lessons": [
                {"title": "¿Qué es Docker y por qué usarlo?", "duration": 15, "is_free": True},
                {"title": "Instalar Docker Desktop/Engine", "duration": 15, "is_free": True},
                {"title": "docker run, pull, stop, rm", "duration": 25},
                {"title": "Imágenes vs contenedores", "duration": 20},
            ]},
            {"title": "Dockerfiles", "lessons": [
                {"title": "Crear tu primer Dockerfile", "duration": 25},
                {"title": "Multi-stage builds", "duration": 30},
                {"title": "Buenas prácticas y capas", "duration": 20},
                {"title": "Variables de entorno y ARG vs ENV", "duration": 20},
            ]},
            {"title": "Docker Compose", "lessons": [
                {"title": "docker-compose.yml: servicios, redes, volumes", "duration": 30},
                {"title": "App multi-servicio: web + db + redis", "duration": 35},
                {"title": "Health checks y depends_on", "duration": 20},
                {"title": "Override files y profiles", "duration": 20},
            ]},
            {"title": "Registries y Distribución", "lessons": [
                {"title": "Docker Hub: push, pull, tags", "duration": 20},
                {"title": "GitHub Container Registry (GHCR)", "duration": 15},
                {"title": "Registry privado", "duration": 20},
                {"title": "Versionado de imágenes", "duration": 15},
            ]},
            {"title": "CI/CD con GitHub Actions", "lessons": [
                {"title": "Crear un workflow básico", "duration": 25},
                {"title": "Build y test automáticos", "duration": 25},
                {"title": "Deploy a VPS con SSH", "duration": 30},
                {"title": "Deploy a Railway / Render / AWS", "duration": 30},
            ]},
            {"title": "Monitoreo y Producción", "lessons": [
                {"title": "Logs con docker logs y json-file", "duration": 20},
                {"title": "Prometheus + Grafana stack", "duration": 35},
                {"title": "Docker networking avanzado", "duration": 25},
                {"title": "Proyecto: Deploy completo con CI/CD", "duration": 40},
            ]},
        ],
    },
    {
        "title": "TypeScript Professional",
        "slug": "typescript-professional",
        "description": "TypeScript a fondo: sistema de tipos, generics, utility types, decorators, módulos, integración con frameworks y patrones de código robusto para producción.",
        "short_description": "Sistema de tipos avanzado, generics, utility types y código robusto.",
        "level": "intermediate",
        "price": 54.99,
        "duration_hours": 42,
        "max_students": 90,
        "is_active": True,
        "is_featured": False,
        "category_slug": "frontend",
        "modules": [
            {"title": "Fundamentos de TypeScript", "lessons": [
                {"title": "¿Por qué TypeScript? Setup con ts-node", "duration": 15, "is_free": True},
                {"title": "Tipos primitivos y anotaciones", "duration": 20},
                {"title": "Interfaces vs Types", "duration": 25},
                {"title": "Arrays, Tuplas y Enums", "duration": 20},
            ]},
            {"title": "Sistema de Tipos Avanzado", "lessons": [
                {"title": "Union types y narrowing", "duration": 25},
                {"title": "Literal types y discriminated unions", "duration": 25},
                {"title": "Type guards y assertion functions", "duration": 25},
                {"title": "Tipos condicionales (Conditional Types)", "duration": 30},
            ]},
            {"title": "Generics", "lessons": [
                {"title": "Funciones genéricas", "duration": 25},
                {"title": "Clases e interfaces genéricas", "duration": 25},
                {"title": "Constraints con extends", "duration": 20},
                {"title": "infer y mapped types", "duration": 30},
            ]},
            {"title": "Utility Types y Patterns", "lessons": [
                {"title": "Partial, Required, Pick, Omit", "duration": 20},
                {"title": "Record, Exclude, Extract, ReturnType", "duration": 25},
                {"title": "Template literal types", "duration": 20},
                {"title": "Builder pattern con TS", "duration": 25},
            ]},
            {"title": "TypeScript en Producción", "lessons": [
                {"title": "tsconfig.json a fondo", "duration": 20},
                {"title": "TS con React (props, events, refs)", "duration": 30},
                {"title": "TS con Node.js + Express", "duration": 25},
                {"title": "Monorepos con TS (project references)", "duration": 25},
            ]},
        ],
    },
]


async def seed():
    """Insert default users and courses."""
    async with async_session() as db:
        try:
            # ── Check if data already exists ────────────────────────────
            existing = await db.execute(select(User).where(User.email == "admin@codeacademypro.com"))
            if existing.scalar_one_or_none():
                print("⚠ Seed data already exists. Skipping.")
                return

            # ── Get or create roles ─────────────────────────────────────
            admin_role_q = await db.execute(select(Role).where(Role.name == "admin"))
            admin_role = admin_role_q.scalar_one_or_none()
            if not admin_role:
                admin_role = Role(name="admin", description="System Administrator")
                db.add(admin_role)

            teacher_role_q = await db.execute(select(Role).where(Role.name == "teacher"))
            teacher_role = teacher_role_q.scalar_one_or_none()
            if not teacher_role:
                teacher_role = Role(name="teacher", description="Instructor")
                db.add(teacher_role)

            student_role_q = await db.execute(select(Role).where(Role.name == "student"))
            student_role = student_role_q.scalar_one_or_none()
            if not student_role:
                student_role = Role(name="student", description="Platform Student")
                db.add(student_role)

            user_role_q = await db.execute(select(Role).where(Role.name == "user"))
            user_role = user_role_q.scalar_one_or_none()
            if not user_role:
                user_role = Role(name="user", description="Registered User (no specific role)")
                db.add(user_role)

            await db.flush()

            # ── Create Admin ────────────────────────────────────────────
            admin = User(
                email="admin@codeacademypro.com",
                username="admin",
                password_hash=hash_password("Admin123!"),
                first_name="Carlos",
                last_name="Administrador",
                status="active",
                email_verified=True,
            )
            db.add(admin)
            await db.flush()
            db.add(UserRole(user_id=admin.id, role_id=admin_role.id))
            print("✅ Admin created: admin@codeacademypro.com / Admin123!")

            # ── Create Teacher ──────────────────────────────────────────
            teacher = User(
                email="ana.garcia@codeacademypro.com",
                username="ana_garcia",
                password_hash=hash_password("Teacher123!"),
                first_name="Ana",
                last_name="García",
                bio="Desarrolladora senior con 10 años de experiencia. Especialista en Python, React y DevOps.",
                status="active",
                email_verified=True,
            )
            db.add(teacher)
            await db.flush()
            db.add(UserRole(user_id=teacher.id, role_id=teacher_role.id))

            # Create Teacher Profile
            teacher_profile = Teacher(user_id=teacher.id, is_active=True)
            db.add(teacher_profile)
            await db.flush()

            print("✅ Teacher created: ana.garcia@codeacademypro.com / Teacher123!")

            # ── Create Demo Student ─────────────────────────────────────
            student = User(
                email="estudiante@codeacademypro.com",
                username="estudiante_demo",
                password_hash=hash_password("Student123!"),
                first_name="Juan",
                last_name="Estudiante",
                status="active",
                email_verified=True,
            )
            db.add(student)
            await db.flush()
            db.add(UserRole(user_id=student.id, role_id=student_role.id))

            # Create Student Profile
            student_profile = Student(user_id=student.id, enrollment_status="active")
            db.add(student_profile)

            print(f"✅ Student created: estudiante@codeacademypro.com / Student123!")

            await db.flush()

            # ── Create Courses ──────────────────────────────────────────
            for course_data in COURSES_DATA:
                # Find category
                cat_slug = course_data.pop("category_slug", None)
                modules_data = course_data.pop("modules", [])

                cat_id = None
                if cat_slug:
                    cat_q = await db.execute(select(Category).where(Category.slug == cat_slug))
                    cat = cat_q.scalar_one_or_none()
                    if not cat:
                        cat = Category(name=cat_slug.capitalize(), slug=cat_slug, is_active=True)
                        db.add(cat)
                        await db.flush()
                    cat_id = cat.id

                course = Course(
                    title=course_data["title"],
                    slug=course_data["slug"],
                    description=course_data["description"],
                    short_description=course_data["short_description"],
                    category_id=cat_id,
                    teacher_id=teacher_profile.id,
                    price=course_data["price"],
                    level=course_data["level"],
                    duration_hours=course_data["duration_hours"],
                    max_students=course_data["max_students"],
                    is_active=course_data["is_active"],
                    is_featured=course_data["is_featured"],
                )
                db.add(course)
                await db.flush()

                # Create modules and lessons
                for m_idx, m_data in enumerate(modules_data):
                    module = Module(
                        course_id=course.id,
                        title=m_data["title"],
                        sort_order=m_idx,
                        is_published=True,
                    )
                    db.add(module)
                    await db.flush()

                    for l_idx, l_data in enumerate(m_data["lessons"]):
                        lesson = Lesson(
                            module_id=module.id,
                            title=l_data["title"],
                            sort_order=l_idx,
                            duration_minutes=l_data.get("duration", 20),
                            is_free=l_data.get("is_free", False),
                            is_published=True,
                        )
                        db.add(lesson)

                total_lessons = sum(len(m["lessons"]) for m in modules_data)
                print(f"✅ Course: {course_data['title']} ({len(modules_data)} modules, {total_lessons} lessons)")

            await db.commit()
            print("\n🎉 Seed completed successfully!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Seed error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())
