# 🔒 Seguridad — CodeAcademy Pro

## Seguridad por Capas

```
┌──────────────────────────────────────────┐
│  Capa 1: Red / Infraestructura           │
│  HTTPS, Firewall, Rate Limiting global   │
├──────────────────────────────────────────┤
│  Capa 2: Aplicación / Middleware         │
│  JWT, RBAC, CORS, CSRF, Rate Limiting    │
├──────────────────────────────────────────┤
│  Capa 3: Validación de Datos             │
│  Pydantic, Sanitización, Regex           │
├──────────────────────────────────────────┤
│  Capa 4: Base de Datos                   │
│  ORM parametrizado, Constraints, RLS     │
├──────────────────────────────────────────┤
│  Capa 5: Archivos / Storage              │
│  MIME validation, Size limits, Signed URLs│
├──────────────────────────────────────────┤
│  Capa 6: Auditoría                       │
│  Logging, Audit trail, Alertas           │
└──────────────────────────────────────────┘
```

---

## Autenticación JWT

### Access Token
- Algoritmo: HS256
- Expiración: 30 minutos
- Payload: `{ sub: user_id, roles: ["student"], iat, exp }`
- Firmado con `JWT_SECRET`

### Refresh Token
- Expiración: 7 días
- Almacenado en Redis (revocable)
- Rotación: cada refresh genera nuevo par access+refresh
- Invalidación en logout

### Flujo
```
1. Login → access_token (30min) + refresh_token (7d)
2. Request → Authorization: Bearer {access_token}
3. Token expirado → POST /refresh con refresh_token
4. Logout → refresh_token eliminado de Redis
```

---

## Hashing de Contraseñas

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # Salt automático

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

- bcrypt con salt automático (12 rounds default)
- Nunca almacenar passwords en texto plano
- Nunca loggear passwords

---

## RBAC (Role-Based Access Control)

### Roles
| Rol | Permisos |
|-----|----------|
| `admin` | Todo el sistema |
| `teacher` | Cursos asignados, alumnos de sus cursos |
| `student` | Su perfil, sus cursos, sus pagos |

### Implementación
```python
from functools import wraps

def require_roles(*roles: str):
    """Decorator para proteger endpoints por rol"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            user_roles = [r.name for r in current_user.roles]
            if not any(r in user_roles for r in roles):
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Uso:
@router.post("/courses")
@require_roles("admin")
async def create_course(...): ...
```

### Permisos granulares (ownership)
- Docente solo edita **sus** cursos
- Alumno solo ve **su** progreso y **sus** pagos
- Verificación en Service Layer, no solo en middleware

---

## Validación y Sanitización

### Regex de Validación

```python
import re

PATTERNS = {
    "email": r"^[^\s@]+@[^\s@]+\.[^\s@]+$",
    "username": r"^[a-zA-Z0-9_]{3,30}$",
    "name": r"^[a-zA-ZÀ-ÿ\s]{2,120}$",
    "text_general": r"^[^<>]{1,2000}$",
    "slug": r"^[a-z0-9-]{3,120}$",
    "uuid": r"^[0-9a-fA-F-]{36}$",
    "url": r"^https?://[^\s]+$",
    "allowed_file": r"^.*\.(jpg|jpeg|png|webp|pdf)$",
}

# Detección de ataques
ATTACK_PATTERNS = {
    "sql_injection": r"(\b)(SELECT|INSERT|DELETE|DROP|UPDATE|UNION|ALTER)(\b)",
    "script_tag": r"<script.*?>",
    "sql_comment": r"(--|#|/\*)",
    "or_1_equal_1": r"(\bor\b|\band\b).*=.*",
    "dangerous_chars": r"[<>{};]",
}
```

### Sanitización con Bleach
```python
import bleach

def sanitize_text(text: str) -> str:
    return bleach.clean(text, tags=[], strip=True)

def sanitize_html(text: str) -> str:
    return bleach.clean(text, tags=["p","br","strong","em","ul","ol","li"], strip=True)
```

### Pydantic Schemas con validación
```python
from pydantic import BaseModel, field_validator
import re

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    first_name: str
    last_name: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", v):
            raise ValueError("Username: 3-30 chars, alphanumeric + underscore")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain a number")
        return v
```

---

## Protección de Archivos

### Tipos permitidos
| Tipo | Extensiones | MIME | Tamaño máx |
|------|------------|------|------------|
| Imagen | .jpg .jpeg .png .webp | image/jpeg image/png image/webp | 5 MB |
| Documento | .pdf | application/pdf | 10 MB |
| Video | .mp4 .webm | video/mp4 video/webm | 500 MB |

### Tipos rechazados
`.exe .sh .bat .js .php .py .rb .zip .tar .gz .rar`

### Validación MIME real
```python
import magic

def validate_file(file: UploadFile) -> bool:
    # 1. Validar extensión
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileType(f"Extension .{ext} not allowed")

    # 2. Validar MIME type real (magic bytes)
    content = await file.read(8192)
    await file.seek(0)
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_MIMES:
        raise InvalidFileType(f"MIME type {mime} not allowed")

    # 3. Validar tamaño
    if file.size > MAX_UPLOAD_BYTES:
        raise FileTooLarge(f"Max size: {MAX_UPLOAD_MB}MB")

    return True
```

---

## Rate Limiting

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| Login | 10 requests | 1 min |
| Register | 5 requests | 1 min |
| Upload proof | 5 requests | 1 min |
| Forgot password | 3 requests | 1 min |
| General API | 100 requests | 1 min |
| Admin actions | 30 requests | 1 min |

Implementado con Redis + `fastapi-limiter`.

---

## CORS
```python
origins = [
    "https://codeacademypro.com",
    "http://localhost:3000",  # dev
]
app.add_middleware(CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE"],
    allow_headers=["Authorization","Content-Type"],
)
```

---

## Firma Interna entre Servicios (Futuro)

```python
import hmac, hashlib, time, json

def sign_request(body: dict, secret: str) -> str:
    timestamp = str(int(time.time()))
    payload = f"{timestamp}.{json.dumps(body, sort_keys=True)}"
    signature = hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{timestamp}.{signature}"

# Header: X-Signature: {timestamp}.{signature}
# No exponer al frontend
# Validar timestamp (±5 min tolerance)
```

---

## Auditoría

### Acciones registradas
`login`, `logout`, `password_change`, `payment_approved`, `payment_rejected`, `course_created`, `course_deleted`, `user_blocked`, `certificate_issued`

### Datos capturados
- `user_id` — quién realizó la acción
- `action` — qué acción
- `entity_type` + `entity_id` — sobre qué entidad
- `details` (JSONB) — datos adicionales
- `ip_address` — IP del cliente
- `user_agent` — navegador/dispositivo
- `created_at` — cuándo
