FROM node:16.13.2-alpine3.15

ARG SPEEDTEST_VERSION=2.0.3

RUN adduser -D speedtest

RUN apk add --update git

WORKDIR /app
COPY src/. .

RUN npm install git+https://github.com/Darrenmeehan/speed-cloudflare-cli.git && \
    apk add --update py-pip && \
    pip install --no-cache-dir -r requirements.txt && \
    chown -R speedtest:speedtest /app && \
    rm -rf \
     /tmp/* \
     /app/requirements

USER speedtest

CMD ["python", "-u", "exporter.py"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:${SPEEDTEST_PORT:=9798}/