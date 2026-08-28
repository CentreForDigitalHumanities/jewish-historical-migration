FROM python:3.12-bookworm AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --no-install-recommends --yes gdal-bin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /backend

COPY requirements.in requirements.txt requirements-dev.in requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

FROM development AS browser-tests

RUN apt-get update \
    && apt-get install --no-install-recommends --yes chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/bin/chromedriver

# Keep the development environment as the default image target.
FROM development AS default
