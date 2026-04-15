# Zircon FRT — OSINT Intelligence Portal

> OSINT data collection, storage, full-text search, brand protection, and monitoring platform.

![Zircon FRT](https://img.shields.io/badge/version-1.0.0-00ff88?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)
![CI](https://github.com/your-org/zircon-frt/actions/workflows/main.yml/badge.svg)

## Features

- 🔍 **Full-text search** — Elasticsearch with AND/OR/NOT, exact phrases, highlighted results
- 📁 **File management** — upload, parse, and index TXT, CSV, JSON, SQL, **PDF, DOCX, XLSX, XML**
- 🛡️ **Brand protection** — typosquatting detection, similarity scoring, alert management
- 👁️ **Monitoring / watchlist** — track IPs, domains, emails, hashes, keywords
- 📤 **Export** — CSV, JSON, PDF for search results, brand alerts, and watchlist
- 🔒 **JWT authentication** — access + refresh tokens, bcrypt password hashing
- 🦠 **ClamAV antivirus** scanning on every upload
- 🔑 **AES-256-GCM encryption** for stored credentials
- 📊 **Real-time dashboard** — WebSocket-powered live notifications
- 🌐 **i18n** — English, Russian, Ukrainian
- 🎨 **Dark cybersecurity UI** — neon green/cyan accents

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Search | Elasticsearch 8.x |
| Task Queue | Celery + Redis 7 |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Reverse Proxy | Nginx |
| Security | JWT, AES-256-GCM, ClamAV, bcrypt |
| PDF Generation | ReportLab |
| File Parsing | PyMuPDF, pdfminer.six, python-docx, openpyxl, lxml |

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/your-org/zircon-frt.git
cd zircon-frt
cp .env.example .env
```

Edit `.env` and set required secrets:

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

### 3. Initialize database

```bash
docker compose exec backend alembic upgrade head
```

### 4. Open the app

Navigate to **http://localhost** and sign in.

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
| `REDIS_URL` | Redis URL | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT signing key (generate!) | — |
| `ENCRYPTION_KEY` | AES-256 key base64 (generate!) | — |
| `POSTGRES_PASSWORD` | PostgreSQL password | — |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost` |
| `MAX_FILE_SIZE_MB` | Max upload file size | `100` |
| `SMTP_HOST` | SMTP server (optional) | — |
| `CLAMAV_HOST` | ClamAV host | `clamav` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional) | — |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Nginx :80                        │
│           /api → backend    /  → frontend               │
└──────────────────┬──────────────────┬───────────────────┘
                   │                  │
        ┌──────────▼───┐   ┌─────────▼────────┐
        │  FastAPI :8000│   │  React SPA        │
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

See [docs/architecture.md](docs/architecture.md) for the full architecture overview.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/architecture.md](docs/architecture.md) | System architecture with diagrams |
| [docs/deployment.md](docs/deployment.md) | Production deployment guide |
| [docs/api-reference.md](docs/api-reference.md) | API endpoints reference |
| [docs/user-guide/en.md](docs/user-guide/en.md) | English user guide |
| [docs/user-guide/ru.md](docs/user-guide/ru.md) | Russian user guide |
| [docs/user-guide/uk.md](docs/user-guide/uk.md) | Ukrainian user guide |

## API Documentation

When running, visit **http://localhost/api/docs** for interactive Swagger UI or **http://localhost/api/redoc** for ReDoc.

## File Parsing Support

| Format | Library | Notes |
|--------|---------|-------|
| TXT / LOG / MD | built-in | Plain text |
| CSV | built-in | All rows |
| JSON | built-in | Pretty-printed |
| SQL | built-in | Raw SQL |
| PDF | PyMuPDF + pdfminer.six | Fallback chain |
| DOCX / DOC | python-docx | Paragraphs + tables |
| XLSX / XLS | openpyxl + pandas | All sheets |
| XML | xml.etree + lxml | Text content |

## Export

After a search or in Brand Protection, use the export buttons:

- **CSV** — spreadsheet-compatible
- **JSON** — machine-readable with full metadata
- **PDF** — formatted report with ReportLab

Endpoints: `GET /api/v1/export/search?q=...&fmt=csv|json|pdf`

## Backup

```bash
docker compose exec backend python scripts/backup_db_and_files.py \
  --backup-dir /backups --keep-days 30
```

## Project Structure

```
zircon-frt/
├── backend/           # FastAPI + Celery
│   ├── app/
│   │   ├── api/v1/    # REST endpoints (auth, files, search, export, brand, monitoring, ...)
│   │   ├── models/    # SQLAlchemy ORM
│   │   ├── services/  # Business logic
│   │   ├── parsers/   # File parsers (PDF, DOCX, XLSX, XML, ...)
│   │   └── tasks/     # Celery tasks
│   ├── scripts/       # Backup and utility scripts
│   └── alembic/       # DB migrations
├── frontend/          # React + TypeScript
│   └── src/
│       ├── pages/     # Dashboard, Search, Files, Brand Protection, ...
│       ├── components/# UI components + ErrorBoundary
│       ├── locales/   # en / ru / uk translations
│       └── api/       # Axios API client
├── docs/              # Documentation
├── nginx/             # Reverse proxy config
├── .github/workflows/ # CI (lint, test, build)
└── docker-compose.yml
```

## CI / CD

GitHub Actions workflow at `.github/workflows/main.yml` runs on push/PR to `main`:

1. **Backend** — Python 3.12, install deps, run pytest
2. **Frontend** — Node 20, `npm ci`, `npm run build`
3. **Docker** — build backend and frontend images

## License

MIT
