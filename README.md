# Speedtest Exporter

Simple **Speedtest exporter** for **Prometheus** written in **Python** using the
official CLI from **Ookla**

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
* [Speedtest CLI by Ookla][1]
2. **Clone repo**

`git clone https://github.com/MiguelNdeCarvalho/speedtest-exporter.git`

3. **Install requirements**

`pip install -r src/requirements.txt`

4. **Execute the exporter**
`python src/exporter.py`

Then just acess the page `http://localhost:9800/` and you will have the metrics.

### Arguments for the Exporter

The following arguments can change the settings of the **exporter**:

#### ServerID

You can set a server and the **exporter** will use that server to do the tests.
[List of Servers][2]

Usage: `--server-id ID`

#### Port

You can set a port where metrics will be exposed. **Default** is `9800`.

Usage: `--port PORT`
  
#### Interval
  
You can set the time between the executions of the tests. **Default:**`300`**(s)**

Usage: `--interval INTERVAL`

## Add to Prometheus

To add the **Speedtest Exporter** to your **Prometheus** just add this to your `prometheus.yml`:

```yml
- job_name: 'speedtest-exporter'
    scrape_interval: 1m
    static_configs:
      - targets: ['localhost:9800']
```

## Grafana Dashboard

The **Grafana Dashboard** can be found [here][3]

[1]: https://www.speedtest.net/pt/apps/cli
[2]: https://williamyaps.github.io/wlmjavascript/servercli.html
[3]: https://grafana.com/grafana/dashboards/13665
