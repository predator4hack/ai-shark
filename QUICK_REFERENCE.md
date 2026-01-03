# AI-Shark Quick Reference Card

## 🚀 Quick Start

### Development Mode

**Option 1: Use Helper Script (Recommended)**
```bash
# Start all services
./docker-helper.sh start

# View available commands
./docker-helper.sh help
```

**Option 2: Direct Docker Compose**
```bash
# Use 'docker compose' (with space) - Modern Docker plugin
docker compose -f docker-compose.dev.yml up --build

# Or use legacy 'docker-compose' (with hyphen) if available
docker-compose -f docker-compose.dev.yml up --build

# Access services:
# React:     http://localhost:3000
# API:       http://localhost:8000
# API Docs:  http://localhost:8000/docs
# Streamlit: http://localhost:8501
```

> **Note:** Modern Docker (v20.10+) uses `docker compose` (plugin) instead of `docker-compose` (standalone)

### Run Tests
```bash
# Backend tests
pytest tests/api/ -v

# Frontend tests
cd frontend && npm test

# With coverage
pytest tests/api/ --cov=src/api
cd frontend && npm run test:coverage
```

### Production Build
```bash
# Build
docker build -f Dockerfile.prod -t ai-shark:latest .

# Run
docker run -p 8080:8080 -e GOOGLE_API_KEY=$GOOGLE_API_KEY ai-shark:latest
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `docker-compose.dev.yml` | Development orchestration |
| `Dockerfile.prod` | Production multi-stage build |
| `.env.example` | Environment variables template |
| `TESTING_GUIDE.md` | Comprehensive testing docs |
| `INTEGRATION_SETUP.md` | Integration setup guide |

---

## 🧪 Test Commands

```bash
# Run specific test file
pytest tests/api/test_pitch_deck_upload.py -v
npm test -- PitchDeckPage.test.tsx

# Watch mode (development)
cd frontend && npm test -- --watch

# Coverage report
pytest tests/api/ --cov=src/api --cov-report=html
open htmlcov/index.html

# Frontend coverage
cd frontend && npm run test:coverage
```

---

## 🐳 Docker Commands

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f api
docker-compose -f docker-compose.dev.yml logs -f frontend

# Rebuild specific service
docker-compose -f docker-compose.dev.yml build api

# Clean up
docker-compose -f docker-compose.dev.yml down -v

# Execute command in container
docker-compose -f docker-compose.dev.yml exec api pytest tests/api/
docker-compose -f docker-compose.dev.yml exec frontend npm test
```

---

## 📊 Project Structure

```
ai-shark/
├── src/api/              # FastAPI backend
│   ├── main.py
│   ├── routers/
│   ├── services/
│   └── schemas/
├── frontend/             # React frontend
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── store/
│       └── tests/
├── tests/api/            # Backend tests
└── docker-compose.dev.yml
```

---

## 🔧 Troubleshooting

### Port conflicts
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Clean rebuild
```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up
```

### Frontend tests fail
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm test
```

---

## 📚 Documentation Index

- [INTEGRATION_SETUP.md](INTEGRATION_SETUP.md) - Task 3 complete guide
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing instructions
- [TASK3_COMPLETION_SUMMARY.md](TASK3_COMPLETION_SUMMARY.md) - What was delivered
- [BACKEND_README.md](BACKEND_README.md) - API documentation
- [FRONTEND_SETUP_COMPLETE.md](FRONTEND_SETUP_COMPLETE.md) - Frontend guide

---

## ✅ Verification

```bash
bash verify_setup.sh
```

---

## 🌐 Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_api_key_here

# Optional (defaults shown)
USE_GCS=false
GCS_BUCKET_NAME=ai-shark-outputs
API_PORT=8000
GEMINI_MODEL=gemini-2.5-flash
```

Copy `.env.example` to `.env` and update values.

---

## 📦 Dependencies

### Install Backend
```bash
# Already done with UV
uv sync
```

### Install Frontend
```bash
cd frontend
npm install
```

---

## 🎯 Common Tasks

### Add new API endpoint
1. Create route in `src/api/routers/`
2. Add schema in `src/api/schemas/`
3. Include router in `src/api/main.py`
4. Add tests in `tests/api/`

### Add new React component
1. Create in `frontend/src/components/`
2. Add tests in `frontend/src/tests/`
3. Import in page or parent component

### Update Redux state
1. Edit slice in `frontend/src/store/slices/`
2. Add tests in `frontend/src/tests/`
3. Use hooks in components

---

**Last Updated:** January 2, 2026
**Status:** ✅ Task 3 Complete
