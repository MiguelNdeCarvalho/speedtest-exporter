FROM python:3.12-slim as build
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Speedtest CLI Version
ARG SPEEDTEST_VERSION=1.2.0

RUN apt-get update && apt-get -y install curl

WORKDIR /app
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY src/. .
RUN pip install --no-cache-dir -r requirements.txt

RUN echo "TARGETPLATFORM=$TARGETPLATFORM BUILDPLATFORM=$BUILDPLATFORM"

RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
        curl -o /tmp/speedtest.tgz https://install.speedtest.net/app/cli/ookla-speedtest-${SPEEDTEST_VERSION}-linux-armhf.tgz; \
    elif [ "$TARGETPLATFORM" = "linux/arm/v6" ]; then \
        curl -o /tmp/speedtest.tgz https://install.speedtest.net/app/cli/ookla-speedtest-${SPEEDTEST_VERSION}-linux-armel.tgz; \
    elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        curl -o /tmp/speedtest.tgz https://install.speedtest.net/app/cli/ookla-speedtest-${SPEEDTEST_VERSION}-linux-aarch64.tgz; \
    else \
        curl -o /tmp/speedtest.tgz https://install.speedtest.net/app/cli/ookla-speedtest-${SPEEDTEST_VERSION}-linux-x86_64.tgz; \
    fi

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