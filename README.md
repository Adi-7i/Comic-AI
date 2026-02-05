# Comic Generation SaaS - Backend

AI-powered comic generation platform with authentication, authorization, and plan enforcement.

## Features

### ✅ Database Layer (Beanie ODM + MongoDB)
- 7 collection models: users, projects, characters, scenes, generations, payments, audit_logs
- Base document with soft delete and timestamps
- UUID-based public IDs for security
- Comprehensive indexing strategy

### ✅ Authentication & Authorization
- **JWT dual-token system** (access + refresh tokens)
- **Password hashing** with bcrypt
- **User registration** and login
- **Token refresh** and logout
- **Plan enforcement** via dependency injection
- **Rate limiting** via generation quotas

### 🔐 Security
- Environment-based configuration
- No sensitive data in JWT payload
- Password complexity validation
- Secure token signing with HS256

### 📊 Plan Tiers
- **FREE**: No generation (view only)
- **PRO**: 3 pages max, watermark required, 50 generations/month
- **CREATIVE**: 10 pages max, no watermark, 200 generations/month

## Project Structure

```
app/
├── core/                      # Core utilities
│   ├── config.py             # Environment configuration
│   ├── security.py           # Password hashing + JWT
│   └── exceptions.py         # Custom exceptions
├── models/                    # Beanie ODM models
│   ├── base.py               # Base document
│   ├── enums.py              # Enum definitions
│   ├── user.py               # User model
│   ├── project.py            # Project model
│   ├── character.py          # Character model
│   ├── scene.py              # Scene model
│   ├── generation.py         # Generation model
│   ├── payment.py            # Payment model
│   └── audit_log.py          # Audit log model
├── schemas/                   # Pydantic schemas
│   ├── auth.py               # Auth request/response
│   └── token.py              # Token schemas
├── services/                  # Business logic
│   ├── auth_service.py       # Authentication
│   └── plan_service.py       # Plan enforcement
├── api/v1/                    # API routes
│   ├── dependencies/
│   │   └── auth.py           # Auth dependencies
│   └── routes/
│       └── auth.py           # Auth endpoints
├── db.py                      # Database initialization
└── main.py                    # FastAPI application

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and set your values
# CRITICAL: Change SECRET_KEY in production!
# Generate with: openssl rand -hex 32
```

### 3. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use your existing MongoDB instance
```

### 4. Run Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or run directly
python -m app.main
```

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login with email/password | No |
| POST | `/api/v1/auth/refresh` | Refresh access token | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |
| POST | `/api/v1/auth/logout` | Logout user | Yes |

### Example: Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

### Example: Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Example: Protected Request

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Using Dependencies

### Require Authentication

```python
from app.api.v1.dependencies.auth import get_current_user, get_active_user

@router.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {"user_id": user.public_id}
```

### Require Specific Plan

```python
from app.api.v1.dependencies.auth import plan_required
from app.models.enums import UserPlan

@router.post("/pro-feature")
async def pro_feature(user: User = Depends(plan_required(UserPlan.PRO))):
    # Only PRO and CREATIVE users can access this
    return {"message": "PRO feature"}
```

### Rate Limiting

```python
from app.api.v1.dependencies.auth import rate_limit_check

@router.post("/generate")
async def generate_comic(user: User = Depends(rate_limit_check)):
    # Check quota before generation
    return {"status": "generating"}
```

## Environment Variables

See `.env.example` for all configuration options.

**Critical Settings**:
- `SECRET_KEY`: JWT signing secret (MUST change in production)
- `MONGODB_URL`: MongoDB connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiry (default: 15)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiry (default: 7)

## Development

### Code Style
- Follow Clean Architecture principles
- Thin routes, business logic in services
- Dependency injection for auth/authorization
- Async everywhere

### Adding New Routes

1. Create route file in `app/api/v1/routes/`
2. Use dependencies for auth/plan enforcement
3. Delegate business logic to services
4. Register router in `app/main.py`

### Testing

```bash
# Run tests (when test suite is added)
pytest tests/ -v

# Test coverage
pytest --cov=app tests/
```

## Security Checklist

- [x] Passwords hashed with bcrypt
- [x] JWT tokens with expiration
- [x] No sensitive data in tokens
- [x] Environment-based secrets
- [x] Plan enforcement at route level
- [x] Rate limiting via quotas
- [ ] HTTPS in production (deploy configuration)
- [ ] Token blacklisting for logout (future enhancement)

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact the development team.
# Comic-AI
