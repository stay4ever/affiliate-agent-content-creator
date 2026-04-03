# ============================================================
#  affiliate-agent-content-creator — Production Dockerfile
# ============================================================
#  Build:  docker build -t affiliate-agent .
#  Run:    docker run --rm \
#            --env ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
#            --env ANTHROPIC_MODEL="claude-haiku-4-5" \
#            -v "$(pwd)/output:/app/output" \
#            affiliate-agent generate --topic "Best running shoes 2025"
#
#  NEVER pass secrets via ENV in this file or bake them into
#  the image. Always inject ANTHROPIC_API_KEY at run time via
#  --env or your orchestrator's secrets manager.
# ============================================================

# Base image pinned to immutable digest for supply-chain safety.
# Tag: python:3.12.10-slim
# To re-pin: docker pull python:3.12.10-slim && docker inspect --format '{{index .RepoDigests 0}}' python:3.12.10-slim
FROM python:3.12.10-slim@sha256:4600f64a4f85916e73088e40e04c2f2a3e8e534fdfbe15fee0963fafc35bdf5c AS base

# System hardening
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── Builder stage: install dependencies ─────────────────────
FROM base AS builder

COPY requirements.txt pyproject.toml README.md LICENSE ./
COPY src/ src/

# Install all dependencies from the hashed lockfile first (reproducible,
# tamper-evident), then install the package itself without re-resolving deps.
RUN pip install --no-cache-dir --prefix=/install --require-hashes -r requirements.txt && \
    pip install --no-cache-dir --prefix=/install --no-deps .

# ── Final stage: lean runtime image ─────────────────────────
FROM base AS runtime

LABEL org.opencontainers.image.source="https://github.com/stay4ever/affiliate-agent-content-creator" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.licenses="MIT"

# Create a non-root user for security.
# Placed here — before COPY — so this layer is cached independently
# of dependency changes and is not invalidated on every pip update.
RUN useradd --no-create-home --shell /bin/false appuser

# Copy only the installed artifacts from the builder
COPY --from=builder /install /usr/local

# Output directory — mounted at run time; created here as a fallback
ENV CONTENT_OUTPUT_DIR=/app/output \
    LOG_LEVEL=INFO

RUN mkdir -p /app/output && chown appuser:appuser /app/output

# Declare the output volume so orchestrators and docker run operators
# receive an explicit signal that this path must be mounted to persist output.
VOLUME ["/app/output"]

USER appuser

# Smoke-test: verify the CLI entry-point is importable.
# HOME=/tmp is required because appuser was created with --no-create-home.
RUN HOME=/tmp content-creator --help

# Health check: validates that ANTHROPIC_API_KEY is present at runtime.
# Lightweight key-presence check avoids importing the full application on
# every interval, preventing false unhealthy states as startup time grows.
# HOME=/tmp prevents XDG path failures for the no-home appuser.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD HOME=/tmp sh -c '[ -n "$ANTHROPIC_API_KEY" ]'

ENTRYPOINT ["content-creator"]
