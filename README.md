# 🧠 AI Psychologue Bot — Dr. Émile

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![aiogram](https://img.shields.io/badge/aiogram-3.15-blue.svg)](https://docs.aiogram.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

A **Telegram bot** powered by OpenAI that plays **Dr. Émile**, a caring
conversational assistant for emotional support — with a full **FastAPI
backend**, **PostgreSQL** persistence, **Redis** quotas, and an **admin
dashboard**.

> ⚠️ **Disclaimer:** This is an AI assistant, not a licensed mental health
> professional. In case of emergency, contact **911**, **999**, **112**, or
> **988** (US).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 Dr. Émile persona | Warm psychologist-style conversations in English |
| 🗄️ PostgreSQL | Conversations saved across restarts |
| ⚡ Redis | Rate limiting + daily message quotas |
| 🔌 REST API | Reusable for web, mobile, or other channels |
| 📊 Admin dashboard | Users, stats, structured event logs |
| 💎 Plans | `free` (30 msg/day) / `premium` (500 msg/day) |
| 🛡️ Safety | Crisis detection + emergency resource guidance |
| 🐳 Docker | One-command deployment with Docker Compose |

---

## 🏗 Architecture

```
┌─────────────┐     HTTP API      ┌─────────────────────────────────┐
│  Telegram   │ ───────────────►  │         FastAPI Backend         │
│  (telegram/)│                   │  chat · quotas · OpenAI · stats │
└─────────────┘                   └──────────┬──────────┬─────────────┘
                                             │          │
                                    ┌────────▼──┐  ┌────▼────┐
                                    │ PostgreSQL │  │  Redis  │
                                    └────────────┘  └─────────┘
```

| Service | Role |
|---------|------|
| `telegram/` | Thin Telegram client (UI only) |
| `backend/` | Business logic, AI, safety rules |
| `postgres` | Users, messages, event logs |
| `redis` | Rate limiting + daily quotas |

---

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Telegram bot token ([@BotFather](https://t.me/BotFather))
- OpenAI API key ([platform.openai.com](https://platform.openai.com/))

### 1. Clone & configure

```bash
git clone https://github.com/nvikou/Ai-psychologue-bot.git
cd Ai-psychologue-bot

cp .env.example .env
# Edit .env with your tokens and API keys
```

### 2. Start all services

```bash
docker compose up -d --build
docker compose logs -f
```

### 3. Test

- Open your bot in Telegram → send `/start`
- API docs → http://localhost:8000/docs
- Admin dashboard → http://localhost:8000/api/v1/admin/dashboard?key=YOUR_ADMIN_API_KEY

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_TOKEN` | ✅ | Telegram bot token |
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `BACKEND_API_KEY` | ✅ | API key for bot/web clients |
| `ADMIN_API_KEY` | ✅ | Admin dashboard & stats |
| `POSTGRES_PASSWORD` | — | Database password (default: `psychologue`) |
| `OPENAI_MODEL` | — | Default: `gpt-4o-mini` |
| `FREE_DAILY_QUOTA` | — | Free plan limit (default: 30) |
| `PREMIUM_DAILY_QUOTA` | — | Premium plan limit (default: 500) |

See [`.env.example`](.env.example) for the full list.

---

## 📡 API Reference

### Chat

```http
POST /api/v1/chat
X-API-Key: YOUR_BACKEND_API_KEY
Content-Type: application/json

{
  "external_id": "telegram:123456789",
  "channel": "telegram",
  "message": "I feel anxious today",
  "username": "john",
  "first_name": "John"
}
```

**Response:**
```json
{
  "reply": "I hear you...",
  "is_crisis": false,
  "quota_remaining": 29
}
```

### Clear history

```http
DELETE /api/v1/chat/history
X-API-Key: YOUR_BACKEND_API_KEY

{
  "external_id": "telegram:123456789",
  "channel": "telegram"
}
```

### Admin endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/admin/stats` | Global statistics |
| `GET` | `/api/v1/admin/users` | User list |
| `GET` | `/api/v1/admin/events` | Recent events |
| `PATCH` | `/api/v1/admin/users/{id}/plan` | Set `free` or `premium` |
| `GET` | `/api/v1/admin/dashboard?key=` | HTML dashboard |

All admin routes require header `X-Admin-Key` or query param `?key=`.

---

## 📁 Project Structure

```
Ai-psychologue-bot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings & system prompt
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── services/            # Chat, OpenAI, quotas, stats
│   │   ├── api/routes/          # REST endpoints
│   │   └── templates/           # Admin dashboard HTML
│   ├── Dockerfile
│   └── requirements.txt
├── telegram/
│   ├── bot.py                   # Telegram entry point
│   ├── handlers.py              # Message handlers
│   ├── api_client.py            # Backend HTTP client
│   ├── config.py                # UI strings & settings
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml           # postgres + redis + api + bot
├── .env.example
└── README.md
```

---

## 💬 Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | New session + safety disclaimer |
| `/help` | Reminder of limits and emergency numbers |
| 🗑️ *Clear history* | Reset conversation memory |

---

## 🔧 Run Without Docker (dev)

**Backend + DB in Docker, bot locally** (recommended if Docker can't reach Telegram):

```bash
# Start backend only
docker compose up -d postgres redis api

# Run bot on your machine
cd telegram
pip install -r requirements.txt
set BACKEND_URL=http://localhost:8000
set BACKEND_API_KEY=your_key
set TELEGRAM_TOKEN=your_token
python bot.py
```

---

## 🔒 Security

- Never commit `.env` (included in `.gitignore`)
- Use strong random strings for `BACKEND_API_KEY` and `ADMIN_API_KEY`
- User message content is not logged in plain text
- Crisis keywords trigger immediate emergency guidance (no OpenAI call)

---

## 📄 License

MIT — feel free to use and modify.

---

## 👤 Author

**nvikou** — [GitHub](https://github.com/nvikou)

If this project helped you, ⭐ star the repo!
