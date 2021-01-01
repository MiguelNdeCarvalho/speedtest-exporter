# Speedtest Exporter

Simple **Speedtest exporter** for **Prometheus** written in **Python** using the official CLI from **Ookla**

## Quick Start

**Docker**:

```bash
docker run -d \
  --name=speedtest-exporter \
  -p 9800:9800 \
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
      - 9800:9800
    restart: unless-stopped
```

Then just acess the page `http://localhost:9800/` and you will have the metrics.

### Environment Variables

The following environment variables configure the exporter:

* `SPEEDTEST_SERVER`
  Custom server ID from Speedtest server list like [https://telcodb.net/explore/speedtest-servers/](https://telcodb.net/explore/speedtest-servers/)

* `SPEEDTEST_PORT`
  Port where metrics will be exposed. **Default:**`9800`

* `SPEEDTEST_INTERVAL`
  Choose the time between the executions of the tests **Default:**`300`**in seconds**

## Grafana Dashboard

The **Grafana Dashboard** can be found [here](https://grafana.com/grafana/dashboards/13665)
