# CodeAcademy Pro — Frontend

Next.js 14+ con App Router.

## Setup

```bash
npx -y create-next-app@latest ./ --typescript --eslint --tailwind --app --src-dir --import-alias "@/*"
```

## Estructura prevista

```
frontend/
├── src/
│   ├── app/
│   │   ├── (public)/           # Landing, catálogo (SSR/SSG)
│   │   │   ├── page.tsx        # Landing page
│   │   │   └── courses/
│   │   │       ├── page.tsx    # Catálogo
│   │   │       └── [slug]/
│   │   │           └── page.tsx # Detalle curso
│   │   ├── (auth)/             # Login, Register
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── student/            # Panel Alumno
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/
│   │   │   ├── courses/
│   │   │   ├── payments/
│   │   │   ├── profile/
│   │   │   ├── certificates/
│   │   │   └── notifications/
│   │   ├── teacher/            # Panel Docente
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/
│   │   │   ├── courses/
│   │   │   └── students/
│   │   ├── admin/              # Panel Admin
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/
│   │   │   ├── courses/
│   │   │   ├── teachers/
│   │   │   ├── students/
│   │   │   ├── payments/
│   │   │   ├── certificates/
│   │   │   ├── categories/
│   │   │   ├── feedback/
│   │   │   ├── audit/
│   │   │   ├── feature-flags/
│   │   │   └── settings/
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/                 # Botones, inputs, modals
│   │   ├── forms/              # Form components
│   │   ├── layout/             # Header, sidebar, footer
│   │   └── dashboard/          # Widgets de dashboard
│   ├── lib/
│   │   ├── api.ts              # API client (fetch wrapper)
│   │   ├── auth.ts             # Auth utilities
│   │   └── utils.ts            # Helpers
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useCourses.ts
│   │   └── useNotifications.ts
│   └── types/
│       └── index.ts            # TypeScript types
├── public/
├── next.config.js
├── tsconfig.json
└── package.json
```

## Notas

- Usar `(public)` route group para páginas sin auth
- Layouts separados por panel (admin, teacher, student)
- API client centralizado en `lib/api.ts`
- Server Components para páginas estáticas (catálogo)
- Client Components para interacciones (formularios, dashboards)
