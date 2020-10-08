# Speedtest Exporter

Simple **Speedtest exporter** for **Prometheus** written in **Python** using the official CLI from **Ookla**

## Quick Start

**Docker**:

```bash
docker run -d \
  --name=speedtest-exporter \
  -p 9112:9112 \
  --restart unless-stopped \
  miguelndecarvalho/speedtest-exporter
```

Via **docker-compose**:

```docker-compose
version: "3.0"
services:
  speedtest-exporter:
    image: miguelndecarvalho/speedtest-exporter
    container_name: speedtest-exporter
    ports:
      - 9112:9112
    restart: unless-stopped
```

Then just acess the page `http://localhost:9112/` and you will have the metrics.

### Environment Variables

The following environment variables configure the exporter:

* `SPEEDTEST_SERVER`
  Custom server ID from Speedtest server list like [https://telcodb.net/explore/speedtest-servers/](https://telcodb.net/explore/speedtest-servers/)
