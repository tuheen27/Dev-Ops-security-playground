FROM python:alpine

# Install required packages for user management, shell, and HEALTHCHECK
RUN apk add --no-cache shadow curl bash

# Install and upgrade pipenv
RUN pip install --upgrade pipenv

# Create non-root user for security
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

# Copy all files
COPY . .

# Ensure entrypoint is executable (crucial for Alpine with non-root user)
RUN chmod +x entrypoint.sh && \
    # Make sure app user can access app directory
    chown -R app:app /app

# Install dependencies
RUN pipenv install --system --deploy

# Create data directory and set permissions
RUN mkdir -p /srv/data && chown -R app:app /srv/data

# Switch to non-root user
USER app

EXPOSE 8080

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]
