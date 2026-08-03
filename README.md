# AI Psychologue Bot

Conversational support assistant for Telegram, backed by a FastAPI
service with LangGraph session control, PostgreSQL, and Redis.

[![CI](https://github.com/nvikou/Ai-psychologue-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/nvikou/Ai-psychologue-bot/actions/workflows/ci.yml) [![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![aiogram](https://img.shields.io/badge/aiogram-3.15-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/) [![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C)](https://langchain-ai.github.io/langgraph/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/) [![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)



---

## About

Users talk to **Dr. Émile** on Telegram. The backend steers each
session through a structured dialogue cycle — listen, explore,
reflect, then advise — using LangGraph and an LLM intent router.
A public landing page only points people to the bot; there is no
web chat.


---

## Features

- Telegram bot (`/start`, `/help`, free-text conversation)
- LangGraph phases with LLM-based routing between turns
- Replies in English, French, and Spanish
- Crisis detection with optional webhook escalation
- Daily quotas (free / premium) and rate limiting
- Message encryption, data export, account deletion, retention purge
- Admin dashboard with JWT auth and audit logs
- Docker Compose stack with healthchecks and CI

---

## Architecture

```
                 ┌────────────┐
  Browser ──────►│   Nginx    │
                 │  :8000     │
                 └─────┬──────┘
                       │
                 ┌─────▼──────┐     ┌────────────┐
  Telegram bot ─►│  FastAPI   │────►│ PostgreSQL │
  (aiogram)      │  + OpenAI  │     └────────────┘
                 │  + LangGraph│     ┌────────────┐
                 └────────────┘────►│   Redis    │
                                    └────────────┘
```

| Service | Role |
|---------|------|
| `nginx` | Public entry on port 8000 |
| `api` | FastAPI application |
| `bot` | Telegram client (calls the API directly) |
| `postgres` | Persistence |
| `redis` | Quotas and rate limits |

```
backend/     API, LangGraph, Alembic, tests
telegram/    Bot client
nginx/       Reverse proxy
scripts/     Database backups
```

---

## Quick start

**Requirements:** Docker, Docker Compose, an OpenAI key, a Telegram
bot token from [@BotFather](https://t.me/BotFather).

```bash
git clone https://github.com/nvikou/Ai-psychologue-bot.git
cd Ai-psychologue-bot
cp .env.example .env
```

Set at least:

```env
TELEGRAM_TOKEN=
TELEGRAM_BOT_USERNAME=
OPENAI_API_KEY=
BACKEND_API_KEY=
ADMIN_API_KEY=
ADMIN_JWT_SECRET=
ENCRYPTION_KEY=
```

```bash
docker compose up -d --build
```

| | |
|--|--|
| Landing | http://localhost:8000/ |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Admin | http://localhost:8000/api/v1/admin/dashboard?key=`ADMIN_API_KEY` |

All configuration options are listed in [`.env.example`](.env.example).
API routes are documented at `/docs` (chat endpoints use `X-API-Key`).

---

## How a session works

```
listen → explore → reflect → advise → explore …
```

Each user message is classified by a short LLM call
(`continue`, `ready_reflect`, `confirm`, `correct`). That intent
decides the next phase. Crisis messages are handled in the service
layer and never go through the therapy graph.

---

## Development

```bash
# migrations
cd backend && alembic upgrade head

# tests
pip install -r requirements.txt && pytest -q

# backup
bash scripts/backup_postgres.sh      # Linux / macOS
./scripts/backup_postgres.ps1        # Windows
```

Tables are also created on API startup if migrations have not been
applied yet.

Webhook mode is supported via `TELEGRAM_WEBHOOK_MODE` (see
`.env.example`). Default Compose setup uses polling.

---

## License

[MIT](LICENSE) © [nvikou](https://github.com/nvikou)
