#speedtest-exporter

## Description

This is a simple **speedtest exporter** for **Prometheus** written in **Python**

## Running the Container

To run the container via **CLI**:

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
