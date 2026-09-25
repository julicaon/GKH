# Smart City MVP — Ticket System Backend

DDD FastAPI backend for resident triage tickets (MAX messenger) and UK dispatcher workflows.

## Structure

- `domain/` — entities, enums, domain services (no FastAPI/SQLAlchemy)
- `application/` — ports (ABC) and use cases
- `infrastructure/` — SQLAlchemy, seed, MAX mocks
- `interfaces/` — FastAPI routers, schemas, deps
- `tests/` — domain + API tests

## Run locally

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
set PYTHONPATH=.   # Windows PowerShell: $env:PYTHONPATH="."
uvicorn interfaces.main:app --reload --port 8000
```

On startup tables are created and seed data is loaded if the DB is empty.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./smart_city.db` | Postgres or SQLite |
| `MAX_MODE` | `mock` | `mock` or `real` |
| `MAX_BOT_TOKEN` | | Required for real MAX mode |
| `JWT_SECRET` | `dev-secret-change-me` | JWT signing key |

## Seed accounts

- `dispatcher_sever` / `sever123` → УК «Северная»
- `dispatcher_yug` / `yug123` → УК «Южная»

## Tests

```bash
cd backend
$env:PYTHONPATH="."
pytest -q
```

No MAX token required (`MAX_MODE=mock`).

## Docker

```bash
docker build -t smart-city-backend .
docker run -p 8000:8000 -e MAX_MODE=mock smart-city-backend
```

Health: `GET /health`
