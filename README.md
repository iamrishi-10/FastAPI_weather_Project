# Country Restricted Weather API

A FastAPI backend that lets authenticated users save up to four Indian cities and fetch and store current weather for them using the free [Open-Meteo](https://open-meteo.com/) API.

## Features

- **Auth:** sign-up and login with JWT bearer tokens (passwords hashed with Argon2 via `pwdlib`).
- **Country-restricted cities:** city names are geocoded through Open-Meteo and only results in India (`IN`) are accepted.
- **Per-user limit:** each user can save a maximum of 4 cities. Duplicates are detected on the canonical city and state name, so "Bangalore" and "Bengaluru" collide.
- **Weather snapshots:** current temperature, apparent temperature, humidity, wind speed and weather code are fetched on demand and stored in PostgreSQL, so you can read the latest snapshot or the full history.

## Tech stack

Python 3.12+, FastAPI, SQLAlchemy 2, PostgreSQL (psycopg2), PyJWT, pwdlib, httpx, openmeteo-requests, uvicorn. Dependencies are managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` and `uv.lock`); a `requirements.txt` is also included.

## Project structure

```
app/
├── main.py              # FastAPI app and router registration
├── create_database.py   # One-off script: creates the "weather_app" database
├── create_tables.py     # One-off script: creates all tables
├── core/                # config (env vars) and security (hashing, JWT)
├── db/                  # engine/session, Base, ORM models
├── dependencies/        # get_current_user auth dependency
├── routes/              # auth, users, allowed cities, weather endpoints
├── schemas/             # Pydantic request/response models
├── services/            # business logic
└── clients/             # Open-Meteo geocoding and forecast client
```

## Getting started

### Prerequisites

- Python 3.12+
- A running PostgreSQL server
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### 1. Install dependencies

```bash
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set `DATABASE_URL` and `JWT_SECRET_KEY` at minimum. See [Configuration](#configuration).

### 3. Create the database and tables

Run these from the project root:

```bash
uv run python -m app.create_database
uv run python -m app.create_tables
```

`create_database` connects to the server in `DATABASE_URL` and creates a database named `weather_app` if it doesn't exist. Your `DATABASE_URL` should point at that database.

### 4. Run the server

```bash
uv run uvicorn app.main:app --reload
```

The API is served at http://127.0.0.1:8000. Interactive docs are at http://127.0.0.1:8000/docs.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | yes | SQLAlchemy PostgreSQL URL, e.g. `postgresql+psycopg2://user:pass@localhost:5432/weather_app` |
| `JWT_SECRET_KEY` | yes | Secret used to sign access tokens |
| `JWT_ALGORITHM` | yes | JWT algorithm, e.g. `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | yes | Access token lifetime in minutes |
| `OPEN_METEO_GEOCODING_URL` | yes | `https://geocoding-api.open-meteo.com/v1/search` |
| `OPEN_METEO_FORECAST_URL` | yes | `https://api.open-meteo.com/v1/forecast` |
| `HTTP_TIMEOUT_SECONDS` | no | Timeout for geocoding requests (default `10.0`) |

Open-Meteo needs no API key. Never commit your real `.env`; it is listed in `.gitignore`.

## API overview

All endpoints other than `/`, `/health` and `/auth/*` require an `Authorization: Bearer <token>` header.

| Method | Path | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| POST | `/auth/signup` | Create an account (`first_name`, `last_name`, `email`, `password`, `confirm_password`) |
| POST | `/auth/login` | Log in with `email` and `password`; returns `access_token` |
| GET | `/users/me` | Current user profile |
| POST | `/users/cities` | Add an allowed city (`{"city_name": "Hyderabad"}`); max 4 per user |
| GET | `/users/cities` | List your allowed cities |
| DELETE | `/users/cities/{city_id}` | Remove an allowed city |
| POST | `/weather/fetch/{city_id}` | Fetch current weather from Open-Meteo and store a snapshot |
| GET | `/weather/latest/{city_id}` | Latest stored snapshot |
| GET | `/weather/history/{city_id}` | All stored snapshots |

### Example

```bash
# Sign up
curl -X POST http://127.0.0.1:8000/auth/signup -H "Content-Type: application/json" \
  -d '{"first_name":"Ada","last_name":"Lovelace","email":"ada@example.com","password":"secret123","confirm_password":"secret123"}'

# Log in and capture the token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","password":"secret123"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Add a city, then fetch its weather (use the city_id returned by the first call)
curl -X POST http://127.0.0.1:8000/users/cities -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"city_name":"Hyderabad"}'
curl -X POST http://127.0.0.1:8000/weather/fetch/1 -H "Authorization: Bearer $TOKEN"
```

## Error responses

| Status | When |
|---|---|
| 400 | City limit (4) reached |
| 401 | Invalid credentials or token |
| 403 | The city belongs to another user |
| 404 | City not found in India, or no stored weather yet |
| 409 | Email already registered, or city already added |
| 503 | Open-Meteo is unreachable or timed out |

## Tests

`pytest` and `pytest-asyncio` are installed, but the `tests/` directory is currently empty.

```bash
uv run pytest
```
