FROM python:3.10.1-alpine3.15

# Speedtest CLI Version
ARG SPEEDTEST_VERSION=1.1.1

# Create user
RUN adduser -D speedtest

WORKDIR /app
COPY src/. .

# Install required modules and Speedtest CLI
RUN pip install --no-cache-dir -r requirements.txt && \
    ARCHITECTURE=$(uname -m) && \
    export ARCHITECTURE && \
    if [ "$ARCHITECTURE" = 'armv7l' ];then ARCHITECTURE="armhf";fi && \
    wget --progress=dot:giga -O /tmp/speedtest.tgz "https://install.speedtest.net/app/cli/ookla-speedtest-${SPEEDTEST_VERSION}-linux-${ARCHITECTURE}.tgz" && \
    tar zxvf /tmp/speedtest.tgz -C /tmp && \
    cp /tmp/speedtest /usr/local/bin && \
    chown -R speedtest:speedtest /app && \
    rm -rf \
     /tmp/* \
     /app/requirements

USER speedtest

CMD ["python", "-u", "exporter.py"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:${SPEEDTEST_PORT:=9798}/