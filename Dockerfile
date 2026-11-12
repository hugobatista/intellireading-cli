FROM ghcr.io/astral-sh/uv:0.13.8@sha256:5cc1805e2426484abca4ad46ea783bab281fdb225fd82d8ce6d66a81254bac85 AS uv-dist

FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90 AS builder

WORKDIR /app

COPY --from=uv-dist /uv /uvx /usr/local/bin/

COPY pyproject.toml uv.lock README.md ./
COPY src src/

RUN uv export --no-dev --no-emit-project -o requirements.txt \
 && uv build

FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

ARG UID=1000
ARG GID=1000
ARG APP_USER=appuser

LABEL org.opencontainers.image.source=https://github.com/hugobatista/intellireading-cli
LABEL security.scan="true"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN addgroup --system --gid ${GID} ${APP_USER} \
 && adduser --system --uid ${UID} --gid ${GID} --home /app --shell /sbin/nologin ${APP_USER} \
 && mkdir -p /app && chown -R ${APP_USER}:${APP_USER} /app

WORKDIR /app

COPY --chown=${UID}:${GID} --from=builder /app/requirements.txt ./
RUN pip install --no-cache --upgrade pip \
 && pip install --no-cache --require-hashes -r ./requirements.txt

COPY --chown=${UID}:${GID} --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

USER ${APP_USER}

HEALTHCHECK --interval=300s --timeout=10s --start-period=5s --retries=3 \
    CMD intellireading --version || exit 1

ENTRYPOINT ["intellireading"]
