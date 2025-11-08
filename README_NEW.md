# Security Playground

![last commit](https://flat.badgen.net/github/last-commit/sysdiglabs/security-playground?icon=github) ![license](https://flat.badgen.net/github/license/sysdiglabs/security-playground) ![docker pulls](https://flat.badgen.net/docker/pulls/sysdiglabs/security-playground?icon=docker)

A minimal Flask-based HTTP service used as a hands-on "security playground" for learning and testing common container and web application vulnerabilities.

Important: this project intentionally exposes dangerous functionality (arbitrary file read/write and command execution). Only run it in an isolated test environment (throwaway VM or sandboxed container). Do NOT run this image on production, on public networks, or on hosts containing sensitive data.

Contents
- Background & Use case
- Quick start (Docker)
- Run locally (development)
- Endpoints and examples
- Security notes and mitigations
- Development & build notes

## Background & use case

This repository intentionally provides insecure endpoints so you can experiment with:

- File read and write vulnerabilities (including path traversal).
- Remote command execution patterns and risks.
- Container hardening and mitigation techniques.

Use cases:
- Security training and capture-the-flag (CTF) exercises.
- Testing scanning tools and runtime detection (IDS/EDR) in an isolated lab.
- Demonstrating safe fixes and mitigations (sandboxing, auth, capability drop).

## Quick start — Docker (recommended for isolation)

Build the image locally:

```powershell
docker build -t security-playground:local .
```

Run the container (binds to port 8080):

```powershell
docker run --rm -p 8080:8080 security-playground:local
```

Then open a new shell and test the health endpoint:

```powershell
curl http://localhost:8080/health
```

Notes:
- The image runs the Flask app with Gunicorn on port 8080 by default.
- Always run this image in an isolated environment and not on production systems.

## Run locally (development)

You can run the Flask app directly for quick development.

Using pipenv (if you prefer):

```powershell
pipenv install --dev
pipenv run gunicorn -b :8080 --workers 2 --threads 4 --worker-class gthread app:app
```

Or with pip (if you don't use pipenv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt   # create requirements.txt if you prefer pinned deps
gunicorn -b :8080 --workers 2 --threads 4 --worker-class gthread app:app
```

## Endpoints and examples

This service exposes several endpoints — they are intentionally unsafe. Examples below are for lab/testing only.

- Health
  - GET /health
  - Response: 200 OK and body `OK`

- Read a file (insecure)
  - GET /<path>
  - Returns the contents of the file at `/<path>` inside the container.
  - Example:

```powershell
curl http://localhost:8080/etc/passwd
```

- Write a file (insecure)
  - POST /<path>
  - Form body: content=<contents>
  - Writes the provided content to `/<path>` inside the container.
  - Example:

```powershell
curl -X POST http://localhost:8080/tmp/hello -d 'content=hello-world'
```

- Execute a command (insecure)
  - POST /exec
  - Form body: command=<command string>
  - WARNING: allows executing arbitrary shell commands in the container.
  - Example (lab only):

```powershell
curl -X POST http://localhost:8080/exec -d 'command=ls -la /'
```

Behavior note: because routes that accept arbitrary paths are defined in the app, route matching order matters. If you find `/exec` not behaving as expected, it may be due to a routing collision with the dynamic write route.

## Security notes & mitigations

This project is intentionally vulnerable. If you want a safer version or to reduce accidental harm, consider the following mitigations:

1. Sandbox file operations
   - Restrict reads/writes to a single application-owned directory (e.g. `/srv/data`) and canonicalize paths with `os.path.abspath` and a base path check.

2. Remove or protect the exec endpoint
   - Avoid shell execution of user input. If command execution is required for testing, use a strict allowlist and `subprocess.run` with `shell=False` and `shlex.split()`.

3. Authentication & authorization
   - Require a token or basic auth for dangerous endpoints.

4. Run the container as a non-root user
   - In the Dockerfile create an unprivileged user and switch to it with `USER`.

5. Pin dependencies and reproducible builds
   - Add `Pipfile.lock` or a `requirements.txt` with pinned versions. Avoid `*` in dependency specifications for production/CI builds.

6. Dockerfile hardening
   - Add a `.dockerignore`, ensure `entrypoint.sh` is executable, add `HEALTHCHECK` and drop capabilities where possible.

7. Network isolation
   - Only run the container in isolated networks or private lab environments.

## Development & build notes

- The repository ships with a `Pipfile`. If you use `pipenv` and want deterministic builds, create and commit a `Pipfile.lock`.
- The `Makefile` includes `build` and `push` targets for Docker image workflows.

## Recommended next steps (safe hardening)

If you'd like, I can:

- Create a locked-down branch where file reads/writes are limited to `/srv/data` and `/exec` is disabled or restricted.
- Update the `Dockerfile` to create a non-root user and add a `HEALTHCHECK` and `.dockerignore`.
- Add basic tests and a minimal `requirements.txt` with pinned dependencies.

Tell me which of these you'd like me to implement and I will make the changes and validate them locally.

---

License: Apache-2.0
