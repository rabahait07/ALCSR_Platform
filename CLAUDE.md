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
    main.py          FastAPI app, CORS, lifespan (creates tables), GET /api/health
    api/v1/          Endpoint routers; router.py aggregates them, mounted at /api/v1
    core/config.py   Settings (pydantic-settings); env vars or backend/.env override defaults
    core/database.py Async engine, AsyncSessionLocal, Base, get_db dependency
    models/          SQLAlchemy ORM models (import each module in models/__init__.py)
    schemas/         Pydantic v2 request/response schemas
    services/        Business logic; routers stay thin and call into services
  tests/             pytest + pytest-asyncio + httpx (ASGITransport)
frontend/
  public/            Static assets served as-is, including all PDF content
  src/lib/api.ts     Shared axios instance (base URL from VITE_API_URL)
  src/               React application
```

- Database: SQLite by default (`sqlite+aiosqlite:///./alcsr.db`, created in `backend/`). Set
  `DATABASE_URL` to a PostgreSQL URL to switch; `postgres://` and `postgresql://` are rewritten to
  the `postgresql+asyncpg://` driver automatically. No code changes are needed.
- Auth: HS256 JWT access tokens, valid for 1440 minutes. `SECRET_KEY` has a development default
  and the app refuses to start with that default when `ENVIRONMENT=production`.
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
   <a href="/pdfs/worksheets/1.1.1/worksheet-1-questions.pdf" target="_blank" rel="noopener noreferrer">
     Worksheet 1 Questions - CPU Components and Registers
   </a>
   ```

   Never build a custom reader modal, embedded viewer, iframe or PDF.js renderer for them.

2. **MCQ grading happens strictly server-side.** Correct answers must never appear in any client
   network payload before the student submits. Schemas that return questions to the client must
   not include the correct option or anything it can be derived from (no `is_correct` flags, no
   answer hashes, no ordering that leaks it). The client submits the chosen options; the server
   grades them and only then returns the score and correct answers. Use separate Pydantic schemas
   for the "question as shown" and "result after grading" shapes.

3. **Coding challenges execute client-side in Pyodide.** Student code runs only in the browser's
   WebAssembly sandbox. The backend never executes, evaluates or imports user-submitted code (no
   `exec`, `eval`, `subprocess`, containers or remote runners), which removes server RCE risk.

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
- Read configuration through `app.core.config.settings`; never call `os.environ` directly.
- Every endpoint declares a `response_model` (or a typed return) built from `app/schemas`.

### Frontend (TypeScript)

- TypeScript strict mode stays on. No `any`, no `@ts-ignore`, no non-null assertions on values
  that can really be null. `npm run build` (which runs `tsc -b`) must pass with zero errors.
- Clean imports: external packages first, then local modules, separated by a blank line. Use
  `import type` (or inline `type`) for type-only imports; `verbatimModuleSyntax` enforces this.
- Function components and hooks only. One component per file, PascalCase file names for
  components, camelCase for hooks and utilities.
- All HTTP calls go through the shared axios instance in `src/lib/api.ts`.
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
`VITE_API_URL` (defaults to `http://localhost:8000`).
