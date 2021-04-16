FROM python:3.9.4-alpine3.12

WORKDIR /app

COPY src/. .

RUN adduser -D speedtest
RUN pip install -r requirements.txt && rm requirements.txt

RUN chown -R speedtest:speedtest /app

USER speedtest

CMD ["python", "-u", "exporter.py"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:${SPEEDTEST_PORT:=9798}/
