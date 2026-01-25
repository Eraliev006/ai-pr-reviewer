## AI PR Reviewer

Webhook-driven, asynchronous AI code reviews for GitHub Pull Requests.

### Demo

- **Video/GIF**: _TODO_ (`docs/demo.gif`)
- **Screenshot**: _TODO_ (`docs/screenshot.png`)

### What it does

AI PR Reviewer receives GitHub Pull Request webhooks, **verifies the HMAC signature**, ensures **idempotent processing**, enqueues work to **Celery**, generates a **structured review** using an LLM, and posts review comments back to the PR via the GitHub API.

Built to demonstrate production-ready backend design: webhooks, idempotency, async workers, DB state, observability.

### Project status

- ✅ **foundation**: repository scaffolding + local Docker setup + stable API shape (`/api/v1/...`)
- 🚧 **in progress**: webhook verification, idempotency, job state machine, async review pipeline (Celery + Redis)

### Features

- **MVP**
  - [ ] GitHub webhook receiver (FastAPI)
  - [ ] HMAC signature verification (`X-Hub-Signature-256`)
  - [ ] Idempotency per delivery (`X-GitHub-Delivery`) + safe retries
  - [ ] Job state machine (queued/running/done/failed)
  - [ ] Async processing via Celery workers
  - [ ] PR diff fetching and chunking
  - [ ] LLM-backed structured review output (JSON schema)
  - [ ] Post review + inline comments back to GitHub PR
  - [ ] JSON logs via structlog (with `request_id`)
  - [ ] Alembic migrations + PostgreSQL persistence
  - [ ] pytest test suite

- **Planned**
  - [ ] GitHub App auth (installation tokens) + least-privilege permissions
  - [ ] Rate limiting + backoff for GitHub/LLM APIs
  - [ ] DLQ + replay tooling for failed jobs
  - [ ] Prompt/versioning + deterministic evaluation fixtures
  - [ ] OpenTelemetry traces + metrics (Prometheus)
  - [ ] Nginx reverse proxy + hardened production deployment
  - [ ] Multi-tenant support (per-repo secrets/config)

### Tech stack

- **Python**: 3.13
- **API**: FastAPI
- **DB**: PostgreSQL
- **Queue/Cache**: Redis
- **Workers**: Celery
- **Infra**: Docker / docker-compose (Nginx later)
- **Migrations**: Alembic
- **Logging**: structlog (JSON)
- **Tests**: pytest

### Architecture (high level)

- **GitHub** sends `pull_request` webhook to `POST /api/v1/webhooks/github`
- **FastAPI**:
  - validates required headers (`X-GitHub-Delivery`, `X-Hub-Signature-256`)
  - verifies payload signature (HMAC SHA-256)
  - stores the event + idempotency key + initial **job state** in PostgreSQL
  - enqueues a Celery job (PR metadata + delivery id)
- **Celery worker**:
  - processes with an at-least-once, **retry-safe pipeline** (idempotent job acquisition + safe retries)
  - fetches PR diff/patch + context via GitHub API
  - computes review plan (files, chunks, risk areas)
  - calls LLM and produces structured output (summary + inline suggestions)
  - posts a PR review and/or comments back to GitHub
  - updates job state in PostgreSQL (queued/running/done/failed)

### API endpoints

#### Health

```bash
curl -sS localhost:8000/api/v1/health
```

Expected response:

```json
{"status":"ok"}
```

#### GitHub webhooks

Receives GitHub webhook deliveries (e.g. `pull_request` events). GitHub includes a unique delivery id and a signature header.

```bash
curl -sS -X POST localhost:8000/api/v1/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-GitHub-Delivery: 00000000-0000-0000-0000-000000000000" \
  -H "X-Hub-Signature-256: sha256=<hex>" \
  --data '{"action":"opened","pull_request":{"number":123},"repository":{"full_name":"org/repo"}}'
```

Notes:

- **Signature**: computed over the raw request body using your webhook secret.
- **Idempotency**: delivery id should be treated as unique; repeated deliveries must not enqueue duplicate reviews.

### Local development (under ~5 minutes)

#### Prerequisites

- **Docker** + **docker compose**
- **Python 3.13**
- **uv** package manager

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 1) Configure environment (`.env.local`)

This repo uses `.env.local` for local config (loaded by docker-compose).

```bash
cat > .env.local <<'EOF'
# Required now
APP_ENV=local
LOG_LEVEL=INFO

# Webhook security
GITHUB_WEBHOOK_SECRET=replace-me

# Postgres (docker-compose local)
POSTGRES_DB=ai_pr_reviewer
POSTGRES_USER=ai_pr_reviewer
POSTGRES_PASSWORD=ai_pr_reviewer
DATABASE_URL=postgresql://ai_pr_reviewer:ai_pr_reviewer@localhost:5432/ai_pr_reviewer

# Redis (Celery broker/backing store)
REDIS_URL=redis://localhost:6379/0

# Later (enable when PR review posting + LLM are implemented)
# GitHub API
# GITHUB_TOKEN=replace-me
# GitHub App (recommended for production)
# GITHUB_APP_ID=
# GITHUB_APP_PRIVATE_KEY_PEM=
# GITHUB_APP_INSTALLATION_ID=
#
# LLM
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4.1-mini
# LLM_API_KEY=replace-me
EOF
```

#### 2) Create venv + lock dependencies (uv)

```bash
uv lock
uv sync --dev
```

#### 3) Start dependencies (Postgres/Redis)

```bash
docker compose -f docker/docker-compose.local.yml --env-file .env.local up -d --build
```

#### 4) Run migrations

```bash
uv run alembic upgrade head
```

#### 5) Run API + worker

API (FastAPI):

```bash
set -a; source .env.local; set +a
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Worker (Celery):

```bash
uv run celery -A app.celery_app worker -l info
```

### Environment variables

#### Required now

- **`APP_ENV`**: `local|staging|prod`
- **`LOG_LEVEL`**: `DEBUG|INFO|WARNING|ERROR`
- **`GITHUB_WEBHOOK_SECRET`**: webhook secret used for HMAC validation
- **`POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD`**: used by the local Postgres container
- **`REDIS_URL`**: Celery broker/result backend

#### Later

- **`GITHUB_TOKEN`**: GitHub token for API calls (dev; replace with GitHub App in production)
- **`GITHUB_APP_*`**: GitHub App credentials (recommended production auth)
- **`LLM_PROVIDER` / `LLM_MODEL` / `LLM_API_KEY`**: LLM configuration

### Testing

Run the full test suite:

```bash
uv run pytest
```

Common options:

```bash
uv run pytest -q
uv run pytest -k webhook
uv run pytest --maxfail=1 -x
```

### Logging & observability

- **Structured logs**: JSON logs via `structlog` (machine-parsable; friendly for Docker/K8s).
- **Request correlation**: a `request_id` is attached to each request and propagated into background jobs where possible.
  - Incoming: `X-Request-ID` (optional)
  - Generated if missing; always included in logs.

### Security notes

- **Webhook authenticity**: verify `X-Hub-Signature-256` against the raw request body using `GITHUB_WEBHOOK_SECRET`.
- **Replay & duplication**: GitHub can retry deliveries; handle via idempotency keyed by `X-GitHub-Delivery`.
- **Secrets**: never commit `.env.local`; use secret managers in production (GitHub Actions secrets, Vault, etc.).
- **Least privilege** (planned): use a GitHub App with only required permissions for PR read + review write.

### Roadmap

- **Short term**
  - Complete end-to-end pipeline: webhook → enqueue → diff → LLM → PR review
  - Harden idempotency + retries + state transitions
  - Add fixtures for deterministic review tests

- **Medium term**
  - GitHub App auth + multi-repo config
  - Observability (metrics/traces) + DLQ
  - Production deploy story (Nginx, health checks, migrations, scaling)

### Contributing

- Keep changes focused and reviewable.
- Add/adjust tests for behavior changes.
- Run locally before opening a PR:

```bash
uv run pytest
```

### License

MIT (placeholder). See `LICENSE` (to be added).
