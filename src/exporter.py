import subprocess
import json
import os
import logging

from flask import Flask
from waitress import serve
from prometheus_client import make_wsgi_app, Gauge

DEFAULT_PORT = 9798
APPLICATION_NAME = "cloudflare-speedtest-exporter"

DOWNLOAD_SPEED_KEY = "Download speed:"
UPLOAD_SPEED_KEY = "Upload speed:"

SPEED_UNIT = "Mbps"

app = Flask(APPLICATION_NAME)


format_string = "level=%(levelname)s datetime=%(asctime)s %(message)s"

logger = logging.getLogger(APPLICATION_NAME)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(format_string)

fh = logging.FileHandler(f"{APPLICATION_NAME}.log", mode="w", encoding="utf-8")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Create Metrics
server = Gauge("speedtest_server_id", "Speedtest server ID used to test")
jitter = Gauge(
    "speedtest_jitter_latency_milliseconds", "Speedtest current Jitter in ms"
)
ping = Gauge("speedtest_ping_latency_milliseconds", "Speedtest current Ping in ms")
download_speed = Gauge(
    "speedtest_download_bits_per_second", "Speedtest current Download Speed in bit/s"
)
upload_speed = Gauge(
    "speedtest_upload_bits_per_second", "Speedtest current Upload speed in bits/s"
)
up = Gauge("speedtest_up", "Speedtest status whether the scrape worked")


def bytes_to_bits(bytes_per_sec):
    return bytes_per_sec * 8


def bits_to_megabits(bits_per_sec):
    megabits_per_sec = round(float(bits_per_sec) * (10 ** -6), 2)
    return str(megabits_per_sec)


def megabits_to_bits(megabits_per_sec):
    bits_per_sec = round(float(megabits_per_sec) * (10 ** 6), 2)
    return str(bits_per_sec)


def is_json(input):
    try:
        json.loads(input)
    except ValueError:
        return False
    return True


def run_speed_test():
    timeout = int(os.environ.get("SPEEDTEST_TIMEOUT", 120))
    cmd = [
        "npx",
        "speed-cloudflare-cli",
    ]
    try:
        logger.debug(f"About to run {' '.join(cmd)}")
        output = subprocess.check_output(cmd, timeout=timeout)
        logger.info(output)
        return output
    except subprocess.CalledProcessError as e:
        output = e.output
        if not is_json(output):
            if len(output) > 0:
                logger.error(
                    "Speedtest CLI Error occurred that" + "was not in JSON format"
                )
            return (0, 0, 0, 0, 0, 0)
    except subprocess.TimeoutExpired:
        logger.error(
            "Speedtest CLI process took too long to complete " + "and was killed."
        )
        return (0, 0, 0, 0, 0, 0)
    except Exception as e:
        logger.error(e)


def parse(output):
    logger.debug("Checking output is correct")
    download_speed_in_mbps = 0
    upload_speed_in_mbps = 0
    download_speed_in_bits_ps = 0
    upload_speed_in_bits_ps = 0
    actual_server = 0
    actual_jitter = 0
    actual_ping = 0

    for line in output.splitlines():
        line = line.decode("utf-8")
        if DOWNLOAD_SPEED_KEY in line:
            download_speed_in_mbps = (
                line.replace(DOWNLOAD_SPEED_KEY, "")
                .replace(SPEED_UNIT, "")
                .replace("\x1b[32m", "")
                .replace("\x1b[0m", "")
                .replace("\n", "")
                .replace("\x1b[1m", "")
                .strip()
            )
            download_speed_in_bits_ps = megabits_to_bits(download_speed_in_mbps)
        if UPLOAD_SPEED_KEY in line:
            upload_speed_in_mbps = (
                line.replace(UPLOAD_SPEED_KEY, "")
                .replace(SPEED_UNIT, "")
                .replace("\x1b[32m", "")
                .replace("\x1b[0m", "")
                .replace("\n", "")
                .replace("\x1b[1m", "")
                .strip()
            )
            upload_speed_in_bits_ps = megabits_to_bits(upload_speed_in_mbps)
        if "Server location:" in line:
            actual_server = (
                line.replace("Server location:", "")
                .replace(SPEED_UNIT, "")
                .replace("\x1b[32m", "")
                .replace("\x1b[0m", "")
                .replace("\n", "")
                .replace("\x1b[1m", "")
                .strip()
            )
        if "Jitter:" in line:
            actual_jitter = (
                line.replace("Jitter:", "")
                .replace("ms", "")
                .replace("\x1b[32m", "")
                .replace("\x1b[0m", "")
                .replace("\n", "")
                .replace("\x1b[1m", "")
                .replace("\x1b[35m", "")
                .strip()
            )
        if "Latency:" in line:
            actual_ping = (
                line.replace("Latency:", "")
                .replace("ms", "")
                .replace("\x1b[32m", "")
                .replace("\x1b[0m", "")
                .replace("\n", "")
                .replace("\x1b[1m", "")
                .replace("\x1b[35m", "")
                .strip()
            )
    # FIXME actual_server is expected to be a number, but is a string from Cloudflare
    actual_server = 0
    return (
        actual_server, actual_jitter, actual_ping,
        download_speed_in_bits_ps, upload_speed_in_bits_ps, 1)


@app.route("/metrics")
def metrics():
    cli_output = run_speed_test()
    r_server, r_jitter, r_ping, r_download, r_upload, r_status = parse(cli_output)
    server.set(r_server)
    jitter.set(r_jitter)
    ping.set(r_ping)
    download_speed.set(r_download)
    upload_speed.set(r_upload)
    up.set(r_status)
    logger.info(
        f"Server={r_server} Jitter={r_jitter} "
        + f"Ping={r_ping} Download={r_download} Upload={r_upload}"
    )
    return make_wsgi_app()


@app.route("/")
def root():
    return (
        f"<h1>Welcome to  {APPLICATION_NAME}.</h1>"
        + "Click <a href='/metrics'>here</a> to see metrics."
    )


def main():
    port = os.getenv("SPEEDTEST_PORT", DEFAULT_PORT)
    logger.info(f"Starting {APPLICATION_NAME}")
    serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
