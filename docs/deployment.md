# Zircon FRT — Deployment Guide

## Prerequisites

- Docker ≥ 24.0 and Docker Compose v2
- 4 GB RAM minimum (8 GB recommended)
- 20 GB disk space

## Quick Start (Production)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/zircon-frt.git
cd zircon-frt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your production values:

```env
# Security — MUST change in production
SECRET_KEY=your-secret-key-minimum-32-characters-long

# Database
POSTGRES_USER=zircon
POSTGRES_PASSWORD=strong-password-here
POSTGRES_DB=zircon
DATABASE_URL=postgresql+asyncpg://zircon:strong-password-here@postgres:5432/zircon

# Redis
REDIS_URL=redis://redis:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# App settings
APP_NAME=Zircon FRT
CORS_ORIGINS=https://yourdomain.com

# Email notifications (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@yourdomain.com

# ClamAV antivirus (optional)
CLAMAV_HOST=clamav
CLAMAV_PORT=3310
```

### 3. Start services

```bash
docker compose up -d
```

### 4. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 5. Create initial admin user

```bash
docker compose exec backend python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import hash_password

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email='admin@yourdomain.com',
            username='admin',
            hashed_password=hash_password('change-me'),
            is_active=True,
            is_admin=True,
        )
        db.add(admin)
        await db.commit()

asyncio.run(create_admin())
"
```

## Service Ports

| Service | Internal Port | Description |
|---------|--------------|-------------|
| nginx | 80, 443 | Public web + API proxy |
| backend | 8000 | FastAPI application |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache/queue |
| elasticsearch | 9200, 9300 | Search engine |

## Docker Compose Services

```yaml
# docker-compose.yml (summary)
services:
  nginx          # Reverse proxy, serves frontend
  backend        # FastAPI application
  worker         # Celery task worker
  beat           # Celery scheduler
  postgres       # PostgreSQL database
  redis          # Redis
  elasticsearch  # Elasticsearch
```

## Upgrading

```bash
git pull origin main
docker compose build backend frontend
docker compose up -d
docker compose exec backend alembic upgrade head
```

## Backup & Restore

### Backup

```bash
docker compose exec backend python scripts/backup_db_and_files.py \
  --backup-dir /backups \
  --keep-days 30
```

### Restore database

```bash
gunzip -c /backups/postgres_20240101_120000.sql.gz | \
  docker compose exec -T postgres psql -U zircon zircon
```

### Restore files

```bash
tar -xzf /backups/uploads_20240101_120000.tar.gz -C /
```

## Scaling Workers

```bash
# Scale Celery workers
docker compose up -d --scale worker=4
```

## Health Checks

```bash
# API health
curl http://localhost/health

# Elasticsearch
curl http://localhost:9200/_cluster/health

# PostgreSQL
docker compose exec postgres pg_isready -U zircon
```

## SSL / TLS

Configure your SSL certificates in `nginx/conf.d/`:

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location /api/ {
        proxy_pass http://backend:8000;
    }

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

## Logs

```bash
# View all logs
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f worker
```

## Monitoring

- API docs: `http://yourdomain.com/api/docs`
- ReDoc: `http://yourdomain.com/api/redoc`
- Elasticsearch: `http://localhost:9200/_cat/indices`
