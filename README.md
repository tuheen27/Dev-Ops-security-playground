# Security Playground

![last commit](https://flat.badgen.net/github/last-commit/sysdiglabs/security-playground?icon=github) ![license](https://flat.badgen.net/github/license/sysdiglabs/security-playground) ![docker pulls](https://flat.badgen.net/docker/pulls/sysdiglabs/security-playground?icon=docker)

A minimal Flask-based HTTP service used as a hands-on "security playground" for learning and testing common container and web application vulnerabilities.

⚠️ **WARNING**: This project intentionally exposes dangerous functionality (arbitrary file read/write and command execution). **Only run it in an isolated test environment** (throwaway VM or sandboxed container). **Do NOT run this image on production systems, public networks, or on hosts containing sensitive data.**

---

## 📋 Table of Contents

- [Background & Use Cases](#background--use-cases)
- [Quick Start (Docker)](#quick-start--docker)
- [Run Locally](#run-locally)
- [API Endpoints](#api-endpoints)
- [Security Notes & Hardening](#security-notes--hardening)
- [Development & Architecture](#development--architecture)
- [Changes & Improvements](#changes--improvements)

---

## Background & Use Cases

This repository intentionally provides insecure endpoints to help you learn about and practice with:

- **File system vulnerabilities** — arbitrary read/write, path traversal, permission checks
- **Command execution risks** — shell injection, timeout handling, subprocess safety
- **Container security** — running as non-root, resource limits, health checks
- **Secure coding patterns** — input validation, error handling, logging

**Ideal for:**
- Security training and capture-the-flag (CTF) exercises
- Testing security scanning tools (SAST, DAST, container scanners)
- Learning defensive programming techniques
- Demonstrating vulnerabilities to teams

---

## Quick Start — Docker

### Build

```powershell
docker build -t security-playground:local .
```

### Run

```powershell
docker run --rm -p 8080:8080 security-playground:local
```

### Test Health

In another terminal:

```powershell
curl http://localhost:8080/health
# Expected output: OK
```

### Verify Running Status

```powershell
docker ps
# Should show the container running on port 8080
```

---

## Run Locally

### Prerequisites

- Python 3.9+
- pipenv or pip

### Option 1: Using pipenv (Recommended)

```powershell
# Install dependencies
pipenv install

# Run the app
pipenv run gunicorn -b :8080 --workers 2 --threads 4 --worker-class gthread app:app
```

### Option 2: Using pip + virtualenv

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app
gunicorn -b :8080 --workers 2 --threads 4 --worker-class gthread app:app
```

Both will start the app on `http://localhost:8080`.

---

## API Endpoints

All endpoints are intentionally insecure for testing. **Examples below are for lab/testing only.**

### 1. Health Check

**GET** `/health`

- **Response**: 200 OK, body: `OK`
- **Purpose**: Container orchestration (Kubernetes, Docker Swarm) health probes

**Example:**

```powershell
curl http://localhost:8080/health
# Output: OK
```

---

### 2. Read a File

**GET** `/<path>`

- **Response**: 200 OK + JSON with file contents
- **Errors**: 404 (not found), 403 (permission denied), 413 (file too large >10 MB)
- **Purpose**: Arbitrary file read vulnerability demo
- **Limitation**: Text files only; binary files return 415 error

**Examples:**

```powershell
# Read a system file
curl http://localhost:8080/etc/hostname

# Expected response (JSON):
{
  "file": "etc/hostname",
  "size": 12,
  "content": "mycontainer\n"
}

# Read a file with errors handled
curl http://localhost:8080/etc/shadow
# Returns 403 (Permission denied) instead of 500 error
```

---

### 3. Write a File

**POST** `/<path>` with form data `content=<data>`

- **Request**: Form parameter `content=<data>`
- **Response**: 201 Created + JSON with status
- **Errors**: 400 (missing content), 403 (permission denied), 413 (content too large >10 MB)
- **Purpose**: Arbitrary file write vulnerability demo

**Examples:**

```powershell
# Write to /tmp
curl -X POST http://localhost:8080/tmp/test.txt -d 'content=hello world'

# Expected response (JSON):
{
  "status": "written",
  "file": "tmp/test.txt",
  "bytes": 11
}

# Verify the write
curl http://localhost:8080/tmp/test.txt
```

---

### 4. Execute a Command

**POST** `/exec` with form data `command=<cmd>`

- **Request**: Form parameter `command=<cmd>`
- **Response**: 200 OK + JSON with stdout, stderr, returncode
- **Errors**: 400 (syntax error), 504 (timeout >10s)
- **Purpose**: Remote command execution vulnerability demo
- **Safety**: Uses `shlex.split()` instead of raw shell; no shell=True

**Examples:**

```powershell
# List directory
curl -X POST http://localhost:8080/exec -d 'command=ls -la /app'

# Expected response (JSON):
{
  "stdout": "total 52\ndrwxr-xr-x ... app\n-rw-r--r-- ... app.py\n...",
  "stderr": "",
  "returncode": 0
}

# Get hostname
curl -X POST http://localhost:8080/exec -d 'command=hostname'

# Verify return code on error
curl -X POST http://localhost:8080/exec -d 'command=ls /nonexistent'
# Returns returncode: 2, stderr populated
```

---

## Security Notes & Hardening

This project is intentionally vulnerable. Below are mitigations and hardening steps:

### 1. Path Sandboxing (Recommended)

**Status**: Not yet implemented. Consider restricting file ops to `/srv/data`:

```python
import os

SANDBOX_DIR = '/srv/data'

def validate_path(user_path):
    """Ensure file access is within sandbox."""
    real_path = os.path.abspath(os.path.join(SANDBOX_DIR, user_path))
    if not real_path.startswith(os.path.abspath(SANDBOX_DIR)):
        raise ValueError("Path traversal attempt")
    return real_path
```

### 2. Command Execution Allowlist

**Status**: Partially implemented (uses `shlex.split()`). Fully secure version:

```python
ALLOWED_COMMANDS = {'ls', 'cat', 'whoami', 'pwd'}

def safe_exec(command):
    cmd_name = shlex.split(command)[0]
    if cmd_name not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {cmd_name}")
    return subprocess.run(shlex.split(command), ...)
```

### 3. Authentication

**Status**: Not implemented. Add for production use:

```python
from functools import wraps

def require_token(f):
    @wraps(f)
    def check_token(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f'Bearer {SECRET_TOKEN}':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return check_token

@app.route('/exec', methods=['POST'])
@require_token
def exec():
    ...
```

### 4. Non-Root User (✅ Implemented)

The Dockerfile now creates a non-root `app` user and runs as `app` instead of `root`.

```dockerfile
RUN groupadd -r app && useradd -r -g app app
USER app
```

### 5. Resource Limits (✅ Implemented)

- File size limit: 10 MB
- Content size limit: 10 MB
- Command timeout: 10 seconds

### 6. Error Handling (✅ Implemented)

- Proper HTTP status codes (404, 403, 400, 500)
- JSON error responses
- No stack traces exposed to client

### 7. Logging (✅ Implemented)

Gunicorn logs all requests to stdout/stderr (viewable with `docker logs`).

### 8. Network Isolation (Manual)

Only run in:
- Isolated Docker networks: `docker network create isolated && docker run --network isolated ...`
- Kubernetes with NetworkPolicies
- Private/internal networks only

---

## Development & Architecture

### Project Structure

```
security-playground/
├── app.py                 # Flask app (90 lines, 4 routes + error handlers)
├── entrypoint.sh          # Container startup (Gunicorn launcher)
├── Dockerfile             # Container definition (non-root user, HEALTHCHECK)
├── requirements.txt       # Pinned Python dependencies
├── Pipfile                # Pipenv source (alternative to requirements.txt)
├── Pipfile.lock           # Locked dependencies (reproducible builds)
├── Makefile               # Build/push automation (versioning, testing)
├── .dockerignore          # Exclude files from build context
├── LICENSE                # Apache-2.0
└── README.md              # This file
```

### Key Technologies

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9 | Runtime |
| Flask | 3.1.0 | Web framework |
| Gunicorn | 23.0.0 | WSGI server (production) |
| Docker | Latest | Containerization |

### Code Highlights

**Route Priority** (crucial for Flask):

1. `/health` (static) — matches first
2. `/exec` (static) — matches second
3. `/<path>` (dynamic catch-all) — matches last

This ensures static routes are never shadowed by dynamic routes.

**Error Handling**:

- All exceptions caught and returned as JSON (500 errors)
- Specific HTTP codes for file not found (404), permissions (403), timeouts (504)
- All responses include error messages for debugging

**Response Format**:

All successful responses use JSON:

```json
{
  "status": "...",
  "file": "...",
  "content": "...",
  "size": 123,
  "bytes": 456,
  "stdout": "...",
  "stderr": "...",
  "returncode": 0
}
```

---

## Changes & Improvements

### Recent Updates (This Session)

1. ✅ **Fixed routing bugs** — static routes now matched before dynamic catch-all
2. ✅ **Added error handling** — proper HTTP codes (404, 403, 400, 500)
3. ✅ **Improved `/exec` safety** — uses `shlex.split()` instead of raw shell, returns JSON
4. ✅ **Hardened Dockerfile** — non-root user, HEALTHCHECK, chmod +x entrypoint.sh
5. ✅ **Created `.dockerignore`** — cleaner build context
6. ✅ **Created `requirements.txt`** — simpler pip-based alternative
7. ✅ **Improved `entrypoint.sh`** — better logging and signal handling
8. ✅ **Enhanced Makefile** — versioning, help, test targets
9. ✅ **Added size limits** — prevent DoS via huge files/content
10. ✅ **Updated README** — comprehensive documentation

### Future Improvements

- [ ] Implement path sandboxing (`/srv/data` restriction)
- [ ] Add command allowlist for `/exec`
- [ ] Implement token-based authentication
- [ ] Add rate limiting per IP
- [ ] Create test suite (pytest)
- [ ] Add Prometheus metrics endpoint
- [ ] Migrate to Python 3.12+ (support longer)
- [ ] Add Alpine-based Dockerfile for smaller images

---

## License

Apache License 2.0 — See `LICENSE` file for details.

---

## Disclaimer

This project is intended for **educational and authorized testing purposes only**. Unauthorized access to computer systems is illegal. Always obtain proper authorization before using this tool in any environment.

---

**Need help?** Check the error responses from endpoints; they include descriptive messages to help debug issues.
