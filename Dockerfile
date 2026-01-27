FROM python:3-slim

# Links Docker image with repository
LABEL org.opencontainers.image.source=https://github.com/hugobatista/intellireading-cli


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore
WORKDIR /app
COPY . /app

RUN pip install --no-cache --upgrade pip \
 && pip install --no-cache /app \
 && addgroup --system app && adduser --system --group app \
 && mkdir -p /tmp/app \
 && chown -R app:app /tmp/app

USER app

VOLUME /tmp/app

ENTRYPOINT ["intellireading"]
