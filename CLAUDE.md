# ALCSR

ALCSR (A-Level Computer Science Revision) is a full-stack e-learning platform tailored to the
OCR H446 specification. Students sign up, then revise by specification topic using worksheets,
multiple-choice quizzes, notes, exam question packs, past papers and Python coding challenges.

## Architecture

| Part | Stack | Location |
| --- | --- | --- |
| Backend | FastAPI, async SQLAlchemy 2, Pydantic v2, JWT auth (python-jose + passlib/bcrypt) | `backend/` |
| Frontend | React + Vite + TypeScript (strict) + Tailwind CSS v3 | `frontend/` |
| Code sandbox | Pyodide (CPython compiled to WebAssembly), running in the browser | `frontend/` |

```
backend/
  app/
    main.py          FastAPI app, CORS, lifespan (creates tables, seeds if empty), GET /api/health
    api/deps.py      DbSession and CurrentUser dependency aliases for endpoint signatures
    api/v1/          Endpoint routers; router.py aggregates them, mounted at /api/v1
    core/config.py   Settings (pydantic-settings); env vars or backend/.env override defaults
    core/database.py Async engine, AsyncSessionLocal, Base, get_db dependency
    core/security.py Password hashing, JWT creation, get_current_user dependency
    models/          SQLAlchemy ORM models (import each module in models/__init__.py)
    schemas/         Pydantic v2 request/response schemas
    services/        Business logic; routers stay thin and call into services
    services/seed.py seed_database(): loads the syllabus and sample content into an empty DB
    services/seed_data/  The seeded content: syllabus, MCQ bank (per paper), challenges
  tests/             pytest + pytest-asyncio + httpx (ASGITransport)
frontend/
  public/            Static assets served as-is
  public/resources/  PDF content (worksheets/, notes/, exam-packs/, past-papers/)
  src/App.tsx        Routes: /login and /signup are public; everything else is protected
  src/services/api.ts  Shared axios instance, token storage, 401 handling, getErrorMessage()
  src/types/         TypeScript interfaces matching the backend's JSON responses
  src/context/       AuthProvider (AuthContext.tsx) and the context object (auth-context.ts)
  src/hooks/         useAuth() and useFetch() (GET with loading, error and reload state)
  src/components/    Shared UI: Navbar, AppLayout, ProtectedRoute, TopicSelector, forms
  src/pages/         One component per route
  src/utils/         Form validation mirroring the backend's rules
```

- Database: SQLite by default (`sqlite+aiosqlite:///./alcsr.db`, created in `backend/`). Set
  `DATABASE_URL` to a PostgreSQL URL to switch; `postgres://` and `postgresql://` are rewritten to
  the `postgresql+asyncpg://` driver automatically. No code changes are needed.
- Auth: HS256 JWT access tokens, valid for 1440 minutes. `SECRET_KEY` has a development default
  and the app refuses to start with that default when `ENVIRONMENT=production`. Signup and login
  take JSON bodies and return a `Token`; the client sends it as `Authorization: Bearer <token>`.
  Protect an endpoint by adding a `current_user: CurrentUser` parameter. Syllabus and resource
  endpoints are public; `/auth/me`, `/dashboard/metrics` and every quiz and challenge endpoint
  require a token.
- API routes (all under `/api/v1`): `auth/signup`, `auth/login`, `auth/me`, `syllabus/tree`,
  `resources/worksheets/{spec_code}`, `resources/notes/{spec_code}`,
  `resources/exam-questions/{section_slug}` (section code with a hyphen, e.g. `1-3`),
  `resources/past-papers`, `quizzes/topics`, `quizzes/{spec_code}`,
  `quizzes/{spec_code}/submit`, `challenges`, `challenges/{slug}`, `challenges/{slug}/submit`,
  `dashboard/metrics`.
- Seeding: on startup the app creates missing tables and, only if there are no syllabus topics,
  loads the 24 OCR H446 sub-topics, sample resources, the MCQ bank and the coding challenges.
  It never changes a database that already has topics, so edits to `services/seed_data/` reach
  an existing database only if you delete `alcsr.db` (development) or migrate the data.
  Every seeded PDF link points at one of four sample files in `frontend/public/resources/`.
- Frontend auth: the JWT is kept in `localStorage` under `alcsr_token` and attached to every
  request by `services/api.ts`. A 401 from any endpoint except `/auth/login` and `/auth/signup`
  clears the token and signs the user out, and `ProtectedRoute` then redirects to `/login`.
  Read the signed-in user with `useAuth()`.
- Frontend routes: `/login`, `/signup`, `/dashboard`, `/worksheets`, `/notes`, `/exam-questions`,
  `/past-papers`, `/mcqs`, `/challenges`. `TopicSelector` links to detail routes
  (`/worksheets/{spec_code}`, `/notes/{spec_code}`, `/mcqs/{spec_code}`,
  `/exam-questions/{section_slug}`) and the challenge list links to `/challenges/{slug}`.
- CORS: only `http://localhost:5173` and `http://127.0.0.1:5173` are allowed by default
  (`CORS_ORIGINS`). The Vite dev server is pinned to port 5173 with `strictPort` to match.
- Content taxonomy: content is organised by OCR H446 paper → section → sub-topic, for example
  Paper 1 → 1.1 → 1.1.1 Structure and Function of the Processor. Paper 1 covers 1.1–1.5 and
  Paper 2 covers 2.1–2.3. The top navigation is Worksheets, MCQs, Notes, Exam Questions,
  Past Papers, Coding Challenges.

## Strict architectural rules

These are non-negotiable. Do not work around them, even temporarily.

1. **PDF content is static and opens by direct link.** All Worksheets, Notes, Exam Question Packs
   and Past Papers (including answers, mark schemes and walkthroughs) are static PDF files. Link to
   them only with a plain anchor:

   ```tsx
   <a href="/resources/worksheets/sample-worksheet.pdf" target="_blank" rel="noopener noreferrer">
     Worksheet 1 Questions - CPU Components and Registers
   </a>
   ```

   Never build a custom reader modal, embedded viewer, iframe or PDF.js renderer for them. The
   `href` is the `file_url` returned by the API; the files live in `frontend/public/resources/`.

2. **MCQ grading happens strictly server-side.** Correct answers must never appear in any client
   network payload before the student submits. Schemas that return questions to the client must
   not include the correct option or anything it can be derived from (no `is_correct` flags, no
   answer hashes, no ordering that leaks it). The client submits the chosen options; the server
   grades them and only then returns the score and correct answers. Use separate Pydantic schemas
   for the "question as shown" and "result after grading" shapes. A quiz is up to 10 random
   questions for a sub-topic; the client posts `{question_id: selected_index}` and the server
   grades whichever of that topic's questions were submitted.

3. **Coding challenges execute client-side in Pyodide.** Student code runs only in the browser's
   WebAssembly sandbox. The backend never executes, evaluates or imports user-submitted code (no
   `exec`, `eval`, `subprocess`, containers or remote runners), which removes server RCE risk.
   The browser runs the challenge's `test_cases` and posts `code`, `passed`, `passed_tests` and
   `total_tests`; the server only stores them. `total_tests` must equal the number of test cases
   for the challenge, and `passed` must be true exactly when every test passed.

## Code style

### Backend (Python)

- Pydantic v2 only: `model_config = ConfigDict(...)`, `field_validator`, `model_validator`,
  `model_validate`, `model_dump`. Never the v1 API (`class Config`, `@validator`, `.dict()`,
  `orm_mode`). Use `ConfigDict(from_attributes=True)` for schemas built from ORM objects.
- Fully async data access: `AsyncSession` from the `get_db` dependency and SQLAlchemy 2 style
  `select()` statements. No sync sessions and no legacy `session.query()`.
- Type-hint every function signature. Use built-in generics (`list[str]`, `dict[str, int]`) and
  `X | None`.
- Clean imports: three groups separated by a blank line (standard library, third-party, `app.*`),
  alphabetised within each group, absolute imports only, no wildcard imports, no unused imports.
- Relationships are not lazy-loaded in async code (it raises `MissingGreenlet`). Load them
  explicitly with `selectinload()` / `joinedload()`, or query the related table directly.
- Enum-like columns (`resource_type`, `difficulty`) are plain strings guarded by CHECK
  constraints. Their allowed values live in `app/models/enums.py`; adding a value means updating
  the enum and migrating the constraint.
- Questions are returned to the client only through `MCQQuestionPublicOut`. Never add
  `correct_index` or `explanation` to it or return `MCQQuestion` data any other way before grading.
- Timestamp columns use `app.models.types.UTCDateTime`, so values are always timezone-aware UTC.
- bcrypt calls (`get_password_hash`, `verify_password`) are slow on purpose; call them through
  `run_in_threadpool` from async code, as `app/services/auth.py` does.
- Read configuration through `app.core.config.settings`; never call `os.environ` directly.
- Every endpoint declares a `response_model` (or a typed return) built from `app/schemas`.

### Frontend (TypeScript)

- TypeScript strict mode stays on. No `any`, no `@ts-ignore`, no non-null assertions on values
  that can really be null. `npm run build` (which runs `tsc -b`) must pass with zero errors.
- Clean imports: external packages first, then local modules, separated by a blank line. Use
  `import type` (or inline `type`) for type-only imports; `verbatimModuleSyntax` enforces this.
- Function components and hooks only. One exported component per file (small private helper
  components may sit beside it), PascalCase file names for components, camelCase for hooks and
  utilities. A component file exports only its component, so hooks and context objects live in
  their own files.
- All HTTP calls go through the shared axios instance in `src/services/api.ts`. Use `useFetch`
  for simple GETs and show failures with `getErrorMessage()`. Type every response with an
  interface from `src/types`.
- Style with Tailwind utilities and the theme tokens in `tailwind.config.js`; do not hard-code
  hex colours in components. Compose conditional classes with `clsx`.

  | Token | Hex | Use |
  | --- | --- | --- |
  | `obsidian` | `#0f0f11` | Page background |
  | `surface` | `#18181b` | Cards and panels |
  | `card-border` | `#27272a` | Card borders and dividers |
  | `brand` / `brand-light` | `#2563eb` / `#3b82f6` | Primary actions / hover, focus, accents |
  | `content-primary` | `#f4f4f5` | Primary text |
  | `content-secondary` | `#a1a1aa` | Secondary text |

- Fonts are self-hosted through `@fontsource`: IBM Plex Sans (`font-sans`) for the interface and
  IBM Plex Mono (`font-mono`) for code. Do not load fonts from an external CDN.
- Tailwind is pinned to v3 (`tailwind.config.js`, `postcss.config.js`, `@tailwind` directives).
  Do not upgrade to v4 without migrating the configuration.

## Commands

Commands are shown for PowerShell on Windows. On macOS/Linux, activate the virtual environment
with `source .venv/bin/activate` instead.

### Backend (run from `backend/`)

```powershell
# One-time setup
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the API at http://localhost:8000 (interactive docs at /docs)
uvicorn app.main:app --reload --port 8000

# Run all tests
pytest

# Run one test file or one test
pytest tests/test_health.py
pytest tests/test_health.py::test_health_check_returns_ok
```

Optional configuration: copy `backend/.env.example` to `backend/.env`.

### Frontend (run from `frontend/`)

```powershell
# One-time setup
npm install

# Dev server at http://localhost:5173
npm run dev

# Type-check and production build
npm run build

# Lint (oxlint)
npm run lint

# Serve the production build locally
npm run preview
```

Optional configuration: copy `frontend/.env.example` to `frontend/.env.local` to change
`VITE_API_URL` (defaults to `http://localhost:8000/api/v1`).
