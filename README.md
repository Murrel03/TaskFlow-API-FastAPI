# TaskFlow API

A REST API for task and project management, built with **FastAPI** and **SQLAlchemy**.
Users register and log in with JWT authentication, create projects, and manage tasks
inside them — with pagination, filtering, ownership checks, and a full pytest suite.

Built as a portfolio project for a Python Developer (backend) role: it demonstrates the
core of a production-shaped FastAPI service — routers, ORM models, Pydantic schemas,
auth, and tests, all separated into their own modules.

## Tech stack

- **Python 3.12**, **FastAPI**, **Uvicorn**
- **SQLAlchemy 2.0** ORM — SQLite by default, PostgreSQL via `DATABASE_URL`
- **Pydantic v2** for request/response validation
- **JWT** auth (PyJWT) with **bcrypt** password hashing
- **pytest** + FastAPI `TestClient` for the test suite
- **Docker** (single-file Dockerfile)

## Features

- Register / login; passwords are bcrypt-hashed, never stored in plain text
- JWT bearer tokens (30-minute expiry by default) protect every project/task route
- Full CRUD for **projects** and **tasks**, scoped to the owning user (403/404 if not yours)
- Task **filtering** by status (`todo` / `in_progress` / `done`), priority, and project
- **Pagination** on list endpoints (`skip` / `limit`, with a `total` count for tasks)
- Proper HTTP errors: 400 duplicate email, 401 bad/missing token, 403 not your project, 404 not found, 422 validation errors
- Interactive Swagger docs generated automatically by FastAPI

## How to run

```bash
cd taskflow-api-python
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# optional: copy .env.example values into your shell / a .env file
uvicorn app.main:app --reload
```

Then open:

- **Swagger UI (interactive docs): http://127.0.0.1:8000/docs**
- Health check: http://127.0.0.1:8000/health

Try it in Swagger: `POST /auth/register` → `POST /auth/login` → click **Authorize**,
paste the `access_token`, then use the project and task endpoints.

To run on PostgreSQL instead of SQLite:

```bash
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/taskflow"
uvicorn app.main:app --reload
```

Or with Docker:

```bash
docker build -t taskflow-api .
docker run -p 8000:8000 taskflow-api
```

## How to run tests

```bash
pytest -q
```

Current status: **18 tests, all passing** — covering registration, duplicate-email and
short-password rejection, login success/failure, unauthenticated and bad-token access,
project/task CRUD, status filtering, pagination, updates, deletes, and 404/422 handling.
Tests run against an isolated in-memory SQLite database (see `tests/conftest.py`), so
they never touch your real data.

## Project structure

```
taskflow-api-python/
├── app/
│   ├── main.py          # FastAPI app, router registration, /health
│   ├── database.py      # engine, session factory, get_db dependency
│   ├── models.py        # SQLAlchemy models: User, Project, Task
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # bcrypt hashing, JWT create/verify, get_current_user
│   └── routers/
│       ├── auth.py      # /auth/register, /auth/login
│       ├── projects.py  # /projects CRUD
│       └── tasks.py     # /tasks CRUD + filtering + pagination
├── tests/
│   ├── conftest.py      # in-memory test DB + auth fixtures
│   ├── test_auth.py     # 7 auth tests
│   └── test_tasks.py    # 11 project/task tests
├── requirements.txt
├── .env.example
└── Dockerfile
```

## Resume bullets (use only after you have run and understood this project yourself)

- Built **TaskFlow API**, a FastAPI REST API for project/task management with JWT authentication (bcrypt-hashed passwords), SQLAlchemy ORM models, and full CRUD with pagination and status/priority filtering; runs on SQLite by default and PostgreSQL via environment config.
- Wrote an **18-test pytest suite** (all passing) covering auth flows, CRUD, filtering, and pagination using FastAPI's TestClient with an isolated in-memory test database; documented the API with auto-generated Swagger docs and containerised it with Docker.

## Interview questions about this project (with short model answers)

**1. How does your JWT authentication flow work, end to end?**
The user registers with an email and password; the password is hashed with bcrypt before
storage. On login, the API verifies the password against the hash and returns a signed
JWT whose `sub` claim is the user's email, expiring in 30 minutes. The client sends it as
`Authorization: Bearer <token>`; a `get_current_user` dependency decodes and verifies the
token on every protected route and loads the user, returning 401 if the token is missing,
expired, or invalid.

**2. How do you manage SQLAlchemy sessions in FastAPI?**
Through a dependency, `get_db`, which creates one `SessionLocal` session per request,
yields it to the route, and closes it in a `finally` block. Routes never create their own
engine or global session, which keeps connections scoped to a request and makes the
dependency easy to override in tests with a test database.

**3. What does Pydantic do in this project, and where does validation happen?**
Every request body and response is a Pydantic schema in `schemas.py`. Incoming data is
validated before the route runs — for example, a password shorter than 8 characters or a
missing task title returns 422 automatically — and response models with
`from_attributes=True` serialise SQLAlchemy objects while guaranteeing fields like the
password hash are never exposed.

**4. How is pagination implemented, and why not return everything?**
List endpoints accept `skip` and `limit` query parameters (validated with FastAPI
`Query`, `limit` capped at 100) and apply `.offset(skip).limit(limit)` on the query. The
tasks endpoint also runs a `count()` on the filtered query and returns `total` alongside
the page of items, so a client can build page controls. Returning everything would get
slower and heavier as data grows; pagination keeps responses bounded.

**5. How did you test the API without touching a real database?**
`tests/conftest.py` creates an in-memory SQLite engine with a `StaticPool`, overrides the
`get_db` dependency with a test session, and recreates the schema before every test.
Fixtures register and log in a user to produce real auth headers, so tests exercise the
full stack — routing, validation, auth, and ORM — through FastAPI's `TestClient`, covering
auth, CRUD, filtering, pagination, and error cases.
