# Zircon FRT — Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Browser)                          │
│              React + Vite + TypeScript + Tailwind CSS            │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS / WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                        Nginx (Reverse Proxy)                     │
│              Static assets  ·  /api/* → backend                 │
└──────────┬───────────────────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python 3.12)                   │
│                                                                   │
│  ┌─────────────┐  ┌────────────┐  ┌──────────────────────────┐  │
│  │  REST API   │  │  WebSocket │  │  Background Workers       │  │
│  │  /api/v1/*  │  │  /ws/*     │  │  (Celery + Redis)         │  │
│  └──────┬──────┘  └─────┬──────┘  └──────────┬───────────────┘  │
│         │               │                      │                  │
│  ┌──────▼───────────────▼──────────────────────▼──────────────┐  │
│  │                   Service Layer                              │  │
│  │  SearchService · FileService · BrandService · Monitoring    │  │
│  └──────┬───────────────────────────────────┬──────────────────┘  │
│         │                                   │                     │
│  ┌──────▼──────┐                   ┌────────▼──────────┐         │
│  │  SQLAlchemy │                   │ Elasticsearch      │         │
│  │  (asyncpg)  │                   │ Full-text search   │         │
│  └──────┬──────┘                   └───────────────────┘         │
└─────────┼────────────────────────────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────────────────────────────┐
│                    Data Layer                                       │
│                                                                    │
│  ┌────────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  PostgreSQL 16 │  │  Redis 7     │  │  Local Filesystem      │  │
│  │  Primary DB    │  │  Cache/Queue │  │  Uploaded Files        │  │
│  └────────────────┘  └──────────────┘  └───────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Frontend
- **Framework**: React 18 with TypeScript, Vite build tool
- **Styling**: Tailwind CSS with custom dark theme
- **State**: Zustand for global auth state, local useState for UI
- **i18n**: react-i18next with English, Russian, Ukrainian locales
- **Routing**: React Router v6

### Backend (FastAPI)
- **API**: RESTful JSON API under `/api/v1/`
- **Auth**: JWT access tokens with refresh (python-jose)
- **ORM**: SQLAlchemy 2.0 async with asyncpg
- **File Parsing**: Extensible parser system supporting TXT, CSV, JSON, SQL, PDF, DOCX, XLSX, XML
- **Export**: CSV, JSON, PDF export for search results and brand alerts (reportlab)

### Celery Workers
- **File indexing**: Parse uploaded files and index to Elasticsearch
- **Brand monitoring**: Scan for typosquatting domains
- **Watchlist monitoring**: Check IP/domain/email watchlist items
- **Notifications**: Email/webhook delivery

### Databases
| Store | Purpose |
|-------|---------|
| PostgreSQL 16 | Users, files metadata, brand watches, alerts, watchlist, notifications |
| Elasticsearch 8 | Full-text search index of file contents |
| Redis 7 | Celery broker + result backend, rate limiting cache |

## Data Flow

### File Upload & Indexing
```
Client → POST /api/v1/files/upload
       → Store file on disk
       → Save metadata to PostgreSQL
       → Enqueue Celery task
       → Worker: parse file (PDF/DOCX/XLSX/etc.)
       → Worker: index content to Elasticsearch
       → WebSocket push: indexing complete
```

### Search
```
Client → GET /api/v1/search?q=...
       → SearchService.search()
       → Elasticsearch query (multi-match + filters)
       → Return ranked hits with snippets
```

### Brand Protection
```
Celery beat → BrandTask.scan_brand_watch()
            → Generate typosquat candidates
            → Check DNS/WHOIS/SSL
            → Compute similarity score
            → Save BrandAlert if threshold exceeded
            → Notify user via WebSocket + email
```

## Security
- Password hashing: bcrypt via passlib
- JWT tokens: HS256, configurable expiry
- File scanning: ClamAV integration (optional)
- Rate limiting: per-IP via Redis
- CORS: configurable allowed origins
- File encryption at rest: AES-256-GCM (optional, via `cryptography`)
