# ============================================================
#  affiliate-agent-content-creator — Production Dockerfile
# ============================================================
#  Build:  docker build -t affiliate-agent .
#  Run:    docker run --rm \
#            --env ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
#            --env ANTHROPIC_MODEL="claude-opus-4-5" \
#            -v "$(pwd)/output:/app/output" \
#            affiliate-agent generate --topic "Best running shoes 2025"
#
#  NEVER pass secrets via ENV in this file or bake them into
#  the image. Always inject ANTHROPIC_API_KEY at run time via
#  --env or your orchestrator's secrets manager.
#
#  NOTE: To further harden the base image, pin to an immutable
#  digest after pulling locally:
#    docker pull python:3.12.10-slim
#    docker inspect python:3.12.10-slim --format '{{index .RepoDigests 0}}'
#  Then replace the FROM line with:
#    FROM python:3.12.10-slim@sha256:<digest> AS base
# ============================================================

FROM python:3.12.10-slim AS base

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

# Install the package and all runtime deps into a prefix we can copy.
# TODO: Once you have committed a requirements.txt lockfile (generated
# via `pip-compile --generate-hashes pyproject.toml -o requirements.txt`),
# replace the lines below with:
#   COPY requirements.txt .
#   RUN pip install --no-cache-dir --prefix=/install --require-hashes -r requirements.txt && \
#       pip install --no-cache-dir --prefix=/install --no-deps .
RUN pip install --no-cache-dir --prefix=/install .

# ── Final stage: lean runtime image ─────────────────────────
FROM base AS runtime

LABEL org.opencontainers.image.source="https://github.com/stay4ever/affiliate-agent-content-creator" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.licenses="MIT"

# Copy only the installed artifacts from the builder
COPY --from=builder /install /usr/local

# Create a non-root user for security
RUN useradd --no-create-home --shell /bin/false appuser

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

# Health check: same rationale — HOME=/tmp prevents XDG path failures.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD HOME=/tmp content-creator --help

ENTRYPOINT ["content-creator"]
