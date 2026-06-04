# =============================================================================
# Stage 0: uv — pinned version for supply chain security
# Pulls the exact uv version specified by UV_VERSION (overridable at build time).
ARG UV_VERSION=0.11.18
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv-dist

# =============================================================================
# Stage 1: Builder — export locked deps and build wheel
FROM python:3.13-slim AS builder
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

COPY --from=uv-dist /uv /uvx /usr/local/bin/

# uv.lock pins every transitive dependency — must be committed
COPY pyproject.toml uv.lock README.md ./
COPY src src/

# Export locked runtime deps with hashes, build the project wheel
RUN uv export --no-dev --no-emit-project -o requirements.txt \
 && uv build

# =============================================================================
# Stage 2: Runtime — minimal image with locked deps + app
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

LABEL org.opencontainers.image.source=https://github.com/hugobatista/intellireading-cli

# Install locked deps with --require-hashes for supply chain integrity
COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache --upgrade pip \
 && pip install --no-cache --require-hashes -r ./requirements.txt

# Install the app wheel (no source in final image)
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl \
 && addgroup --system app && adduser --system --group app \
 && mkdir -p /tmp/app \
 && chown -R app:app /tmp/app

USER app

VOLUME /tmp/app

ENTRYPOINT ["intellireading"]
