import subprocess
import json
import os
import logging
import dataclasses
import datetime
import uuid

from prometheus_client import make_wsgi_app, Gauge
from flask import Flask
from waitress import serve
from shutil import which

MILLISECOND = datetime.timedelta(milliseconds=1)

app = Flask("Speedtest-Exporter")  # Create flask app

# Setup logging values
format_string = 'level=%(levelname)s datetime=%(asctime)s %(message)s'
logging.basicConfig(encoding='utf-8',
                    level=logging.DEBUG,
                    format=format_string)

# Disable Waitress Logs
log = logging.getLogger('waitress')
log.disabled = True

# Create Metrics
server = Gauge(
    'speedtest_server_id',
    'Speedtest server ID used to test',
    labelnames=('result_uuid',),
)
jitter = Gauge(
    'speedtest_jitter_latency_milliseconds',
    'Speedtest current Jitter in ms',
    labelnames=('result_uuid',),
)
ping = Gauge(
    'speedtest_ping_latency_milliseconds',
    'Speedtest current Ping in ms',
    labelnames=('result_uuid',),
)
download_speed = Gauge(
    'speedtest_download_bits_per_second',
    'Speedtest current Download Speed in bit/s',
    labelnames=('result_uuid',),
)
upload_speed = Gauge(
    'speedtest_upload_bits_per_second',
    'Speedtest current Upload speed in bits/s',
    labelnames=('result_uuid',),
)
up = Gauge(
    'speedtest_up',
    'Speedtest status whether the scrape worked',
    labelnames=('result_uuid',),
)
duration = Gauge(
    'speedtest_duration_milliseconds',
    'Speedtest duration in milliseconds',
    labelnames=('result_uuid',),
)

# Cache metrics for how long (seconds)?
cache_seconds = int(os.environ.get('SPEEDTEST_CACHE_FOR', 0))
cache_until = datetime.datetime.fromtimestamp(0)

# Disable failed metrics
DISABLE_FAILED_METRICS = os.environ.get('DISABLE_FAILED_METRICS', False)


@dataclasses.dataclass
class SpeedtestResult:
    server: int
    jitter: float
    ping: float
    download: float
    upload: float
    uuid: str
    up: int
    duration: int


def bytes_to_bits(bytes_per_sec):
    return bytes_per_sec * 8


def bits_to_megabits(bits_per_sec):
    megabits = round(bits_per_sec * (10**-6), 2)
    return str(megabits) + "Mbps"


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def milliseconds(duration: datetime.timedelta) -> float:
    return duration / MILLISECOND


def failed(start: datetime.datetime) -> SpeedtestResult:
    return SpeedtestResult(
        server=0,
        jitter=0,
        ping=0,
        download=0,
        upload=0,
        uuid=str(uuid.uuid4()),
        up=0,
        duration=milliseconds(now() - start),
    )


def runTest() -> SpeedtestResult:
    start = now()

    serverID = os.environ.get('SPEEDTEST_SERVER')
    timeout = int(os.environ.get('SPEEDTEST_TIMEOUT', 90))

    cmd = [
        "speedtest", "--format=json-pretty", "--progress=no",
        "--accept-license", "--accept-gdpr"
    ]
    if serverID:
        cmd.append(f"--server-id={serverID}")
    try:
        output = subprocess.check_output(cmd, timeout=timeout)
    except subprocess.CalledProcessError as e:
        output = e.output
        if not is_json(output):
            if len(output) > 0:
                logging.error('Speedtest CLI Error occurred that' +
                              'was not in JSON format')
            return failed(start)
    except subprocess.TimeoutExpired:
        logging.error('Speedtest CLI process took too long to complete ' +
                      'and was killed.')
        return failed(start)

    if is_json(output):
        data = json.loads(output)
        if "error" in data:
            # Socket error
            print('Something went wrong')
            print(data['error'])
            return failed(start)
        if "type" in data:
            if data['type'] == 'log':
                print(str(data["timestamp"]) + " - " + str(data["message"]))
            if data['type'] == 'result':
                return SpeedtestResult(
                    server=int(data['server']['id']),
                    jitter=data['ping']['jitter'],
                    ping=data['ping']['latency'],
                    download=bytes_to_bits(data['download']['bandwidth']),
                    upload=bytes_to_bits(data['upload']['bandwidth']),
                    uuid=data.get('result', {}).get('id', str(uuid.uuid4())),
                    up=1,
                    duration=milliseconds(now() - start),
                )


@app.route("/metrics")
def updateResults():
    global cache_until

    if datetime.datetime.now() > cache_until:
        result = runTest()

        logging.info(
            "Server=" + str(result.server) + " " +
            "Jitter=" + str(result.jitter) + "ms " +
            "Ping=" + str(result.ping) + "ms " +
            "Download=" + bits_to_megabits(result.download) + " " +
            "Upload=" + bits_to_megabits(result.upload) + " " +
            "Duration=" + str(result.duration) + "ms " +
            "UUID=" + str(result.uuid)
        )

        if not result.up and DISABLE_FAILED_METRICS:
            logging.info("Skipping failed metrics")
            return

        server.labels(result_uuid=result.uuid).set(result.server)
        jitter.labels(result_uuid=result.uuid).set(result.jitter)
        ping.labels(result_uuid=result.uuid).set(result.ping)
        download_speed.labels(result_uuid=result.uuid).set(result.download)
        upload_speed.labels(result_uuid=result.uuid).set(result.upload)
        up.labels(result_uuid=result.uuid).set(result.up)
        duration.labels(result_uuid=result.uuid).set(result.duration)

        cache_until = datetime.datetime.now() + datetime.timedelta(
            seconds=cache_seconds)

    return make_wsgi_app()


@app.route("/")
def mainPage():
    return ("<h1>Welcome to Speedtest-Exporter.</h1>" +
            "Click <a href='/metrics'>here</a> to see metrics.")


def checkForBinary():
    if which("speedtest") is None:
        logging.error("Speedtest CLI binary not found. Please install it by" +
                      " going to the official website.\n" +
                      "https://www.speedtest.net/apps/cli")
        exit(1)
    speedtestVersionDialog = (subprocess.run(['speedtest', '--version'],
                              capture_output=True, text=True))
    if "Speedtest by Ookla" not in speedtestVersionDialog.stdout:
        logging.error("Speedtest CLI that is installed is not the official" +
                      " one. Please install it by going to the official" +
                      " website.\nhttps://www.speedtest.net/apps/cli")
        exit(1)


if __name__ == '__main__':
    checkForBinary()
    PORT = os.getenv('SPEEDTEST_PORT', 9798)
    logging.info("Starting Speedtest-Exporter on http://localhost:" +
                 str(PORT))
    serve(app, host='0.0.0.0', port=PORT)
