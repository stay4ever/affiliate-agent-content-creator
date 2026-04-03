# ============================================================
#  affiliate-agent-content-creator — Production Dockerfile
# ============================================================
#  Build:  docker build -t affiliate-agent .
#  Run:    docker run --rm \
#            --env ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
#            --env ANTHROPIC_MODEL="claude-opus-4-20250514" \
#            -v "$(pwd)/output:/app/output" \
#            affiliate-agent generate --topic "Best running shoes 2025"
#
#  NEVER pass secrets via ENV in this file or bake them into
#  the image. Always inject ANTHROPIC_API_KEY at run time via
#  --env or your orchestrator's secrets manager.
# ============================================================

FROM python:3.12-slim AS base

# System hardening
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── Builder stage: install dependencies ─────────────────────
FROM base AS builder

COPY pyproject.toml README.md LICENSE ./
COPY src/ src/

# Install the package and all runtime deps into a prefix we can copy
RUN pip install --no-cache-dir --prefix=/install .

# ── Final stage: lean runtime image ─────────────────────────
FROM base AS runtime

# Copy only the installed artifacts from the builder
COPY --from=builder /install /usr/local

# Create a non-root user for security
RUN useradd --no-create-home --shell /bin/false appuser

# Output directory — mounted at run time; created here as a fallback
ENV CONTENT_OUTPUT_DIR=/app/output \
    LOG_LEVEL=INFO

RUN mkdir -p /app/output && chown appuser:appuser /app/output

USER appuser

# Smoke-test: verify the CLI entry-point is importable
RUN content-creator --help

ENTRYPOINT ["content-creator"]
