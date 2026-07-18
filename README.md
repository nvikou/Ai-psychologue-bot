# AI Psychologue Bot

Telegram + web conversational assistant inspired by **Dr. Émile**,
with a FastAPI backend, PostgreSQL, Redis, Nginx, GDPR controls,
and an admin dashboard.

[![CI](https://github.com/nvikou/Ai-psychologue-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/nvikou/Ai-psychologue-bot/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> **Important:** This is an AI assistant, not a licensed mental health
> professional. In an emergency call **911 / 999 / 112 / 988 / 3114**.

---

## Features

- Telegram bot (polling or webhook) + simple web chat UI
- FastAPI REST API reusable by web/mobile clients
- PostgreSQL persistence + Alembic migrations
- Redis quotas, user rate limits, and IP rate limiting
- Message encryption at rest (`ENCRYPTION_KEY`)
- GDPR: export, delete account, retention purge
- Multilingual replies (`en` / `fr` / `es`)
- Crisis detection + optional admin webhook escalation
- Admin dashboard, JWT/admin-key auth, audit logs
- Nginx reverse proxy, Docker healthchecks
- Optional Sentry monitoring
- Pytest suite + GitHub Actions CI
- PostgreSQL backup scripts

---

## Architecture

```text
Browser / Telegram
        │
        ▼
   Nginx (:8000)
        │
        ▼
   FastAPI API
   ├── chat / profile / GDPR
   ├── OpenAI + i18n + crisis
   └── admin dashboard
        │            │
        ▼            ▼
   PostgreSQL      Redis
```

---

## Quick start

```bash
git clone https://github.com/nvikou/Ai-psychologue-bot.git
cd Ai-psychologue-bot
cp .env.example .env
# fill TELEGRAM_TOKEN, OPENAI_API_KEY, BACKEND_API_KEY,
# ADMIN_API_KEY, ENCRYPTION_KEY, ADMIN_JWT_SECRET

docker compose up -d --build
docker compose logs -f
```

| Target | URL |
|---|---|
| Web chat | http://localhost:8000/ |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Privacy | http://localhost:8000/privacy |
| Terms | http://localhost:8000/terms |
| Admin dashboard | http://localhost:8000/api/v1/admin/dashboard?key=ADMIN_API_KEY |

---

## Main API

All chat routes require `X-API-Key`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat` | Send a message |
| `DELETE` | `/api/v1/chat/history` | Clear history |
| `PUT` | `/api/v1/chat/profile` | Update language/goals/notifications |
| `POST` | `/api/v1/chat/gdpr/export` | Export user data |
| `POST` | `/api/v1/chat/gdpr/delete` | Delete account (right to erasure) |
| `POST` | `/api/v1/admin/token` | Exchange admin key for JWT |
| `POST` | `/api/v1/admin/retention/purge` | Purge expired messages |
| `PATCH` | `/api/v1/admin/users/{id}/plan` | Set free/premium |

---

## Telegram webhook mode

In `.env`:

```env
TELEGRAM_WEBHOOK_MODE=true
WEBHOOK_URL=https://your-public-domain
WEBHOOK_PATH=/telegram/webhook
WEBHOOK_PORT=8080
```

Expose the bot container port `8080` (or terminate TLS via Nginx) and
point Telegram to `WEBHOOK_URL + WEBHOOK_PATH`.

---

## Migrations

```bash
cd backend
alembic upgrade head
```

On first Docker start, tables are also created via SQLAlchemy metadata
as a bootstrap fallback.

---

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

---

## Backups

```bash
# Linux/macOS
bash scripts/backup_postgres.sh

# Windows PowerShell
./scripts/backup_postgres.ps1
```

---

## Security & GDPR

- Never commit `.env`
- Set strong `BACKEND_API_KEY`, `ADMIN_API_KEY`, `ADMIN_JWT_SECRET`,
  `ENCRYPTION_KEY`
- Messages can be encrypted at rest
- Retention controlled by `MESSAGE_RETENTION_DAYS` (default 90)
- Admin actions are written to `admin_audit_logs`
- Optional `CRISIS_WEBHOOK_URL` for human escalation alerts
  (no message content included)

---

## License

MIT — see [LICENSE](LICENSE).

Maintained by [nvikou](https://github.com/nvikou).
