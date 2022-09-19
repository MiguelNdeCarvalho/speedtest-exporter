FROM python:3.10-slim as build

# Speedtest CLI Version
ARG SPEEDTEST_VERSION=1.2.0

RUN apt-get update && apt-get -y install curl

WORKDIR /app
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY src/. .
RUN pip install --no-cache-dir -r requirements.txt

ADD https://install.speedtest.net/app/cli/ookla-speedtest-${SPEEDTEST_VERSION}-linux-x86_64.tgz /tmp/speedtest.tgz
RUN tar zxvf /tmp/speedtest.tgz -C /tmp && \
    cp /tmp/speedtest /usr/local/bin

RUN groupadd -g 999 speedtest && \
    useradd -u 999 -d /app -g speedtest speedtest

RUN chown speedtest:speedtest /app

USER speedtest
WORKDIR /app

ENV PATH="/app/venv/bin:$PATH"
CMD ["python", "-u", "exporter.py"]

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:${SPEEDTEST_PORT:=9798}/health
