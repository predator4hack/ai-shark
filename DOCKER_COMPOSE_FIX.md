# Docker Compose Version Issue - Fixed ✅

## Problem

You encountered this error:
```
Error response from daemon: client version 1.43 is too old. Minimum
supported API version is 1.44, please upgrade your client to a newer
version
```

## Root Cause

- **Your Docker version:** 29.1.3 (very new, requires API v1.44+)
- **Your Docker Compose version:** v2.23.3 (older, uses API v1.43)
- **Mismatch:** Docker Compose is too old for your Docker version

## Solution

You have **3 options** to fix this:

---

## ✅ Option 1: Use Built-in Docker Compose Plugin (EASIEST)

Modern Docker includes Compose as a plugin. Just use `docker compose` (with space) instead of `docker-compose` (with hyphen):

```bash
# Instead of this:
docker-compose -f docker-compose.dev.yml up --build

# Use this:
docker compose -f docker-compose.dev.yml up --build
```

**Or use the helper script (recommended):**
```bash
./docker-helper.sh start
```

The helper script automatically detects which version to use.

---

## ✅ Option 2: Upgrade Docker Compose Standalone

If you prefer using `docker-compose` (with hyphen), upgrade to the latest version:

```bash
# 1. Download latest version
curl -fsSL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /tmp/docker-compose

# 2. Make it executable
chmod +x /tmp/docker-compose

# 3. Install (requires sudo password)
sudo mv /tmp/docker-compose /usr/local/bin/docker-compose

# 4. Verify
docker-compose --version
# Should show: Docker Compose version v5.0.1 or newer
```

---

## ✅ Option 3: Create an Alias

If you want to keep using `docker-compose` but with the plugin:

```bash
# Add alias to your shell
echo "alias docker-compose='docker compose'" >> ~/.bashrc
source ~/.bashrc

# Now docker-compose commands will use the plugin
docker-compose -f docker-compose.dev.yml up --build
```

---

## Quick Reference

### Using the Helper Script

We've created a helper script that handles this automatically:

```bash
# Start services
./docker-helper.sh start

# Stop services
./docker-helper.sh stop

# View logs
./docker-helper.sh logs

# Run tests
./docker-helper.sh test

# See all commands
./docker-helper.sh help
```

### Available Helper Commands

| Command | Description |
|---------|-------------|
| `start` | Start all services (API + Frontend + Streamlit) |
| `stop` | Stop all services |
| `restart` | Restart all services |
| `logs` | View logs from all services |
| `logs-api` | View API logs only |
| `logs-fe` | View Frontend logs only |
| `test` | Run all tests (backend + frontend) |
| `test-api` | Run backend tests only |
| `test-fe` | Run frontend tests only |
| `build` | Rebuild all containers |
| `clean` | Stop and remove all containers and volumes |
| `shell-api` | Open shell in API container |
| `shell-fe` | Open shell in Frontend container |
| `status` | Show running containers |
| `prod-build` | Build production Docker image |

---

## Verification

After applying any solution, verify it works:

```bash
# Check Docker version
docker --version
# Expected: Docker version 29.1.3 or newer

# Check Compose version (if using standalone)
docker-compose --version
# Expected: Docker Compose version v5.0.1 or newer

# Check Compose plugin
docker compose version
# Expected: Docker Compose version v2.32.0 or newer

# Test with our project
docker compose -f docker-compose.dev.yml config
# Should show configuration without errors
```

---

## Recommended Approach

**We recommend Option 1** - using the built-in plugin with the helper script:

1. **Use the helper script for all operations:**
   ```bash
   ./docker-helper.sh start
   ./docker-helper.sh test
   ./docker-helper.sh logs
   ```

2. **Or use `docker compose` directly:**
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   docker compose -f docker-compose.dev.yml down
   ```

This approach:
- ✅ Requires no additional installation
- ✅ Always uses the correct version
- ✅ Is the modern Docker standard
- ✅ Works automatically with your Docker 29.1.3

---

## Updated Documentation

All documentation has been updated to support both approaches:
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Updated with helper script usage
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing instructions
- [INTEGRATION_SETUP.md](INTEGRATION_SETUP.md) - Setup guide

---

## Troubleshooting

### Issue: `docker compose` not found

**Solution:**
Your Docker might not have the plugin. Update Docker:
```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Issue: Helper script not executable

**Solution:**
```bash
chmod +x docker-helper.sh dev-start.sh
```

### Issue: Still getting API version error

**Solution:**
Restart Docker daemon:
```bash
sudo systemctl restart docker
```

---

## Next Steps

Now that the issue is fixed, you can:

1. **Start the development environment:**
   ```bash
   ./docker-helper.sh start
   ```

2. **Access the services:**
   - React UI: http://localhost:3000
   - FastAPI Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Streamlit (legacy): http://localhost:8501

3. **Run tests:**
   ```bash
   ./docker-helper.sh test
   ```

---

## Summary

✅ **Problem Identified:** Docker Compose version mismatch
✅ **Solution Provided:** Use `docker compose` plugin or upgrade standalone
✅ **Helper Script Created:** `docker-helper.sh` for easy management
✅ **Documentation Updated:** All guides now include both methods

You're all set! 🚀
