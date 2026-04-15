# Zircon FRT — API Reference

Interactive API documentation is available at runtime:

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

## Authentication

All endpoints (except `/api/v1/auth/login` and `/api/v1/auth/register`) require a Bearer token:

```http
Authorization: Bearer <access_token>
```

Obtain a token via `POST /api/v1/auth/login`.

---

## Endpoints Summary

### Auth — `/api/v1/auth`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create a new user account |
| POST | `/login` | Obtain access + refresh tokens |
| POST | `/refresh` | Refresh access token |
| GET | `/me` | Get current user profile |
| PUT | `/me` | Update current user profile |

### Files — `/api/v1/files`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/upload` | Upload a file (multipart/form-data) |
| GET | `/` | List uploaded files (paginated) |
| GET | `/{file_id}` | Get file metadata |
| DELETE | `/{file_id}` | Delete a file |
| GET | `/{file_id}/download` | Download file |

### Search — `/api/v1/search`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Full-text search across indexed files |

**Query parameters:**
- `q` (required): Search query, supports Elasticsearch query syntax
- `file_type`: Filter by file extension
- `date_from` / `date_to`: Date range filter
- `page` / `per_page`: Pagination

### Export — `/api/v1/export`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/search` | Export search results |
| GET | `/brand/{watch_id}/alerts` | Export brand alerts |
| GET | `/monitoring/watchlist` | Export watchlist items |

**Query parameters:**
- `fmt`: `csv` (default), `json`, or `pdf`
- `q`: Search query (for `/search` endpoint)

### Dashboard — `/api/v1/dashboard`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/stats` | Platform statistics summary |

### Brand Protection — `/api/v1/brand`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/watches` | List brand watches |
| POST | `/watches` | Create a brand watch |
| GET | `/watches/{id}` | Get brand watch details |
| DELETE | `/watches/{id}` | Delete a brand watch |
| POST | `/watches/{id}/scan` | Trigger manual scan |
| GET | `/watches/{id}/alerts` | List alerts for a watch |
| PUT | `/alerts/{alert_id}` | Update alert status |

### Monitoring — `/api/v1/monitoring`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/watchlist` | List watchlist items |
| POST | `/watchlist` | Add watchlist item |
| PUT | `/watchlist/{id}` | Update watchlist item |
| DELETE | `/watchlist/{id}` | Delete watchlist item |
| GET | `/events` | List monitoring events |

### Notifications — `/api/v1/notifications`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List notifications |
| PUT | `/{id}/read` | Mark notification as read |
| PUT | `/read-all` | Mark all as read |

### Integrations — `/api/v1/integrations`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List configured integrations |
| POST | `/` | Add integration |
| PUT | `/{id}` | Update integration |
| DELETE | `/{id}` | Delete integration |

### WebSocket — `/ws/notifications`

Real-time notification push. Authenticate with `?token=<access_token>`.

```javascript
const ws = new WebSocket(`wss://yourdomain.com/ws/notifications?token=${token}`)
ws.onmessage = (e) => console.log(JSON.parse(e.data))
```

---

## Common Response Formats

### Success

```json
{
  "id": 1,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Error

```json
{
  "detail": "Error message"
}
```

### Paginated list

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

---

## Rate Limiting

The API enforces rate limits per IP address. Exceeded limits return `429 Too Many Requests`.

Default limits:
- 100 requests/minute for authenticated endpoints
- 10 requests/minute for auth endpoints
