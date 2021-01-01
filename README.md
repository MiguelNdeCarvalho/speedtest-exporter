# Speedtest Exporter

Simple **Speedtest exporter** for **Prometheus** written in **Python** using the official CLI from **Ookla**

## Setting up the Exporter

### Via **docker(cli)**

```bash
docker run -d \
  --name=speedtest-exporter \
  -p 9800:9800 \
  --restart unless-stopped \
  miguelndecarvalho/speedtest-exporter
```

### Via **docker-compose**

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

### Manually

1. **Requirements**
* Git installed;
* Python3 installed;
* Pip installed;
* [Speedtest CLI by Ookla](https://www.speedtest.net/pt/apps/cli)
2. **Clone repo**

`git clone https://github.com/MiguelNdeCarvalho/speedtest-exporter.git`

3. **Install requirements**

`pip install -r src/requirements.txt`

4. **Execute the exporter**
`python src/exporter.py`

Then just acess the page `http://localhost:9800/` and you will have the metrics.

### Settings for the Exporter

The following environment variables configure the exporter:

* `SPEEDTEST_SERVER`
  Custom server ID from Speedtest server list like [https://telcodb.net/explore/speedtest-servers/](https://telcodb.net/explore/speedtest-servers/)

* `SPEEDTEST_PORT`
  Port where metrics will be exposed. **Default:**`9800`

* `SPEEDTEST_INTERVAL`
  Choose the time between the executions of the tests **Default:**`300`**in seconds**

## Add to Prometheus

To add the **Speedtest Exporter** to your **Prometheus** just add this to your `prometheus.yml`:

```yml
- job_name: 'speedtest-exporter'
    scrape_interval: 1m
    static_configs:
      - targets: ['localhost:9800']
```

## Grafana Dashboard

The **Grafana Dashboard** can be found [here](https://grafana.com/grafana/dashboards/13665)
