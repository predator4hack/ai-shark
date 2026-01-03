# Testing Guide - AI-Shark Migration

This guide covers all testing aspects for the Streamlit to React migration.

## Table of Contents

1. [Backend Testing](#backend-testing)
2. [Frontend Testing](#frontend-testing)
3. [Integration Testing](#integration-testing)
4. [Docker Testing](#docker-testing)
5. [Testing Checklist](#testing-checklist)

---

## Backend Testing

### Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install test dependencies (if not already installed)
pip install pytest pytest-cov httpx
```

### Running Backend Tests

```bash
# Run all backend tests
pytest tests/api/

# Run with coverage
pytest tests/api/ --cov=src/api --cov-report=html

# Run specific test file
pytest tests/api/test_pitch_deck_upload.py

# Run with verbose output
pytest tests/api/ -v

# Run only unit tests (skip integration tests)
pytest tests/api/ -m "not integration"
```

### Backend Test Structure

```
tests/
├── conftest.py                      # Shared fixtures
├── api/
│   ├── __init__.py
│   ├── test_pitch_deck_upload.py    # Upload endpoint tests
│   ├── test_storage_manager.py      # Storage backend tests
│   └── test_job_manager.py          # Job management tests
└── fixtures/
    └── sample_deck.pdf              # Test fixtures
```

### Backend Test Coverage

- ✅ Health check endpoint
- ✅ Pitch deck upload (valid PDF, PPT, PPTX)
- ✅ File type validation
- ✅ File size validation (100MB limit)
- ✅ Job status polling
- ✅ File download endpoints
- ✅ Storage manager (local and GCS)
- ✅ Job manager (create, update, cleanup)
- ✅ Error handling

---

## Frontend Testing

### Setup

```bash
cd frontend

# Install test dependencies (if not already installed)
npm install
```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Run tests in watch mode (during development)
npm test -- --watch

# Run with UI (interactive mode)
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- src/tests/PitchDeckPage.test.tsx
```

### Frontend Test Structure

```
frontend/src/
├── tests/
│   ├── setup.ts                    # Test setup and configuration
│   ├── testUtils.tsx               # Custom render with providers
│   ├── PitchDeckPage.test.tsx      # Page component tests
│   ├── DragDropZone.test.tsx       # Upload component tests
│   └── pitchDeckSlice.test.ts      # Redux store tests
└── ...
```

### Frontend Test Coverage

- ✅ PitchDeckPage rendering
- ✅ File upload functionality
- ✅ Drag and drop zone
- ✅ Processing status display
- ✅ Error handling
- ✅ Download links
- ✅ Job status polling
- ✅ Redux state management
- ✅ Component validation

---

## Integration Testing

### End-to-End Test Scenarios

#### Scenario 1: Successful Upload and Processing

```bash
# 1. Start services
docker-compose -f docker-compose.dev.yml up

# 2. Open browser to http://localhost:3000
# 3. Upload a valid PDF pitch deck
# 4. Verify:
#    - Upload progress indicator appears
#    - Status polls every 2 seconds
#    - Company name is displayed
#    - Files are listed with download links
#    - Downloads work correctly
```

#### Scenario 2: Error Handling

```bash
# 1. Upload invalid file type (.txt)
# 2. Verify:
#    - Error message: "Invalid file type"
#    - UI allows retry

# 3. Upload file > 100MB
# 4. Verify:
#    - Error message: "File too large"
```

#### Scenario 3: Network Resilience

```bash
# 1. Start upload
# 2. Stop API container
# 3. Verify:
#    - Error handling in frontend
#    - Can retry after API restart
```

---

## Docker Testing

### Development Environment

```bash
# Build and start all services
docker-compose -f docker-compose.dev.yml up --build

# Expected services:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Streamlit (legacy): http://localhost:8501

# Verify each service health:
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "ai-shark-api"}

# Check frontend loads
curl http://localhost:3000
# Expected: HTML page with React root

# Check API documentation
open http://localhost:8000/docs
# Expected: FastAPI Swagger UI
```

### Testing with Docker Compose

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f api
docker-compose -f docker-compose.dev.yml logs -f frontend

# Execute tests inside containers
docker-compose -f docker-compose.dev.yml exec api pytest tests/api/
docker-compose -f docker-compose.dev.yml exec frontend npm test

# Stop services
docker-compose -f docker-compose.dev.yml down

# Clean up (remove volumes)
docker-compose -f docker-compose.dev.yml down -v
```

### Production Build Testing

```bash
# Build production image
docker build -f Dockerfile.prod -t ai-shark:prod .

# Run production container
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e USE_GCS=false \
  ai-shark:prod

# Test production deployment
curl http://localhost:8080/health
curl http://localhost:8080/
# Expected: React app served from FastAPI

# Test API endpoints
curl http://localhost:8080/api/v1/jobs/test-job-id/status
```

---

## Testing Checklist

### Backend Tests

- [ ] All pytest tests pass
- [ ] Code coverage > 80%
- [ ] Health check endpoint works
- [ ] File upload accepts PDF, PPT, PPTX
- [ ] File type validation rejects invalid files
- [ ] File size limit enforced (100MB)
- [ ] Job status polling works
- [ ] Storage manager saves files locally
- [ ] Job manager creates and tracks jobs
- [ ] Error responses have correct status codes

### Frontend Tests

- [ ] All Vitest tests pass
- [ ] Code coverage > 70%
- [ ] Page renders without errors
- [ ] Drag and drop zone accepts files
- [ ] Upload shows progress indicator
- [ ] Status polling updates UI
- [ ] Error messages display correctly
- [ ] Download links work
- [ ] Redux state updates correctly
- [ ] Component validation works

### Integration Tests

- [ ] Docker Compose starts all services
- [ ] API accessible at http://localhost:8000
- [ ] Frontend accessible at http://localhost:3000
- [ ] File upload end-to-end works
- [ ] Processing completes successfully
- [ ] Downloads work from frontend
- [ ] Error handling works end-to-end
- [ ] Multiple uploads work correctly

### Production Build Tests

- [ ] Production Docker image builds successfully
- [ ] Image size is reasonable (< 2GB)
- [ ] React static files are served
- [ ] API endpoints work
- [ ] Health check responds
- [ ] Environment variables are read correctly
- [ ] GCS storage can be enabled
- [ ] No development dependencies in production image

### Performance Tests

- [ ] File upload handles 100MB files
- [ ] Processing completes in reasonable time (< 5 min)
- [ ] Status polling doesn't overload API
- [ ] Multiple concurrent uploads work
- [ ] Memory usage is acceptable
- [ ] No memory leaks in long-running containers

### Security Tests

- [ ] No secrets in Docker images
- [ ] Non-root user runs the application
- [ ] File upload validates file types
- [ ] File size limits are enforced
- [ ] CORS is properly configured
- [ ] Error messages don't leak sensitive info

---

## Common Issues and Solutions

### Issue: Backend tests fail with "Job not found"

**Solution:**
```bash
# Make sure job_manager is using a fresh instance for each test
# Check conftest.py has proper setup/teardown
```

### Issue: Frontend tests timeout

**Solution:**
```bash
# Increase timeout in test
await waitFor(() => {...}, { timeout: 10000 })

# Or check if API mocks are properly configured
```

### Issue: Docker Compose fails to start

**Solution:**
```bash
# Check ports are not already in use
lsof -i :8000
lsof -i :3000

# Rebuild containers
docker-compose -f docker-compose.dev.yml build --no-cache

# Check logs
docker-compose -f docker-compose.dev.yml logs
```

### Issue: Production build is too large

**Solution:**
```bash
# Check .gcloudignore is properly configured
# Verify multi-stage build is copying only necessary files
docker images ai-shark:prod
```

---

## Continuous Testing

### Pre-commit Checks

```bash
# Run before committing
pytest tests/api/ && cd frontend && npm test && cd ..
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: pytest tests/api/
      - name: Run frontend tests
        run: cd frontend && npm test
```

---

## Next Steps

After completing all tests:

1. Document any failures and create issues
2. Update test coverage reports
3. Add more edge case tests as needed
4. Set up automated testing in CI/CD
5. Create performance benchmarks
6. Test with real production data (anonymized)

---

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Docker Testing Best Practices](https://docs.docker.com/develop/dev-best-practices/)
