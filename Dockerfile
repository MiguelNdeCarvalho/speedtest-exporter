FROM python:3.10.1-alpine3.15

# Speedtest CLI Version
ENV VERSION=1.1.1

WORKDIR /app

COPY src/. .

RUN adduser -D speedtest
RUN pip install -r requirements.txt && \
    export ARCHITECTURE=$(uname -m) && \
    if [ "$ARCHITECTURE" == 'armv7l' ]; then export ARCHITECTURE=armhf; fi && \
    wget -O /tmp/speedtest.tgz "https://install.speedtest.net/app/cli/ookla-speedtest-${VERSION}-linux-${ARCHITECTURE}.tgz" && \
    tar zxvf /tmp/speedtest.tgz -C /tmp && \
    cp /tmp/speedtest /usr/local/bin && \
    rm requirements.txt

RUN chown -R speedtest:speedtest /app

USER speedtest

CMD ["python", "-u", "exporter.py"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:${SPEEDTEST_PORT:=9798}/