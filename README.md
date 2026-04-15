# Zircon FRT — OSINT Intelligence Portal

> **Phase 1 MVP** — Automated OSINT data collection, storage, full-text search, and monitoring platform.

![Zircon FRT](https://img.shields.io/badge/version-1.0.0-00ff88?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)

## Features

- 🔍 **Full-text search** across all files with Elasticsearch (AND/OR/NOT operators, exact phrases, highlighted results)
- 📁 **File management** — upload, parse, and index TXT/CSV/JSON/SQL files
- 🔒 **JWT authentication** with access + refresh tokens
- 🛡️ **ClamAV antivirus** scanning on every upload
- 🔑 **AES-256 encryption** for stored API credentials
- 📊 **Dashboard** with stats and quick actions
- 🌐 **i18n** — English, Russian, Ukrainian
- 🎨 **Dark cybersecurity UI** — neon green/cyan accents

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + FastAPI + SQLAlchemy (async) |
| Database | PostgreSQL 16 |
| Search | Elasticsearch 8.x |
| Task Queue | Celery + Redis 7 |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Reverse Proxy | Nginx |
| Security | JWT, AES-256-GCM, ClamAV |

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/oss0018/zircon-frt.git
cd zircon-frt
cp .env.example .env
```

Edit `.env` and set the required secrets:

```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate AES-256 encryption key
python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

### 2. Start all services

```bash
docker compose up -d --build
```

### 3. Initialize database and admin user

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/init_db.py
```

### 4. (Optional) Seed demo data

```bash
docker compose exec backend python scripts/seed_demo_data.py
```

### 5. Open the app

Navigate to **http://localhost** and sign in with your admin credentials.

## Development Setup

```bash
# Use dev overrides (hot-reload, exposed ports)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Frontend dev server (with HMR)
cd frontend && npm install && npm run dev

# Backend dev server
cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async URL | `postgresql+asyncpg://...` |
| `ELASTICSEARCH_URL` | Elasticsearch endpoint | `http://elasticsearch:9200` |
| `REDIS_URL` | Redis URL (Celery broker) | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT signing key (generate!) | — |
| `ENCRYPTION_KEY` | AES-256 key base64 (generate!) | — |
| `POSTGRES_PASSWORD` | PostgreSQL password | — |
| `ADMIN_EMAIL` | Initial admin email | `admin@zircon.local` |
| `ADMIN_PASSWORD` | Initial admin password | — |
| `CLAMAV_HOST` | ClamAV host | `clamav` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost` |
| `MAX_FILE_SIZE_MB` | Max upload file size | `100` |
| `SMTP_HOST` | SMTP server (optional) | — |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional) | — |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Nginx :80                        │
│           /api → backend    /  → frontend               │
└──────────────────┬──────────────────┬───────────────────┘
                   │                  │
        ┌──────────▼───┐   ┌─────────▼────────┐
        │  FastAPI :8000│   │  React SPA :3000  │
        │  (uvicorn)    │   │  (nginx static)   │
        └──────┬────────┘   └──────────────────┘
               │
   ┌───────────┼───────────┬──────────────┐
   │           │           │              │
   ▼           ▼           ▼              ▼
PostgreSQL Elasticsearch  Redis       ClamAV
  :5432       :9200       :6379        :3310
                            │
                     ┌──────┴──────┐
                     │   Celery    │
                     │  (worker +  │
                     │   beat)     │
                     └─────────────┘
```

## API Documentation

When running, visit **http://localhost/api/docs** for the interactive Swagger UI.

Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | Get JWT tokens |
| POST | `/api/v1/auth/register` | Create account |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/files/upload` | Upload file |
| GET | `/api/v1/files/` | List files |
| POST | `/api/v1/search/` | Full-text search |
| GET | `/api/v1/dashboard/stats` | Dashboard stats |

## File Processing Pipeline

1. **Upload** → file saved to disk, SHA-256 hash computed
2. **Celery task** dispatched → `process_uploaded_file`
3. **ClamAV scan** → quarantine if infected
4. **Parse** → extract text content (TXT/CSV/JSON/SQL)
5. **Elasticsearch index** → file searchable immediately

## Project Structure

```
zircon-frt/
├── backend/           # FastAPI + Celery
│   ├── app/
│   │   ├── api/v1/    # REST endpoints
│   │   ├── models/    # SQLAlchemy ORM
│   │   ├── services/  # Business logic
│   │   ├── parsers/   # File parsers
│   │   └── tasks/     # Celery tasks
│   └── alembic/       # DB migrations
├── frontend/          # React + TypeScript
│   └── src/
│       ├── pages/     # Dashboard, Search, Files, Settings
│       ├── components/# UI components
│       └── api/       # Axios API client
├── nginx/             # Reverse proxy config
└── docker-compose.yml
```

## License

MIT
