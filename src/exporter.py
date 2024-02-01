import subprocess
import json
import os
import logging
import datetime
from prometheus_client import make_wsgi_app, Gauge
from flask import Flask
from waitress import serve
from shutil import which

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
server = Gauge('speedtest_server_id', 'Speedtest server ID used to test')
jitter = Gauge('speedtest_jitter_latency_milliseconds',
               'Speedtest current Jitter in ms')
ping = Gauge('speedtest_ping_latency_milliseconds',
             'Speedtest current Ping in ms')
download_speed = Gauge('speedtest_download_bits_per_second',
                       'Speedtest current Download Speed in bit/s')
upload_speed = Gauge('speedtest_upload_bits_per_second',
                     'Speedtest current Upload speed in bits/s')
up = Gauge('speedtest_up', 'Speedtest status whether the scrape worked')

# Cache metrics for how long (seconds)?
cache_seconds = int(os.environ.get('SPEEDTEST_CACHE_FOR', 0))
cache_until = datetime.datetime.fromtimestamp(0)


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


def runTest():
    serverID = os.environ.get('SPEEDTEST_SERVER')
    interface = os.environ.get('SPEEDTEST_INTERFACE')
    ip = os.environ.get('SPEEDTEST_IP')
    host = os.environ.get('SPEEDTEST_HOST')
    precision = os.environ.get('SPEEDTEST_PRECISION')
    timeout = int(os.environ.get('SPEEDTEST_TIMEOUT', 90))

    cmd = [
        "speedtest", "--format=json-pretty", "--progress=no",
        "--accept-license", "--accept-gdpr"
    ]
    if serverID:
        cmd.append(f"--server-id={serverID}")
    if interface:
        cmd.append(f"--interface={interface}")
    if ip:
        cmd.append(f"--id={ip}")
    if host:
        cmd.append(f"--host={host}")
    if precision:
        cmd.append(f"--precision={precision}")
    try:
        output = subprocess.check_output(cmd, timeout=timeout)
    except subprocess.CalledProcessError as e:
        output = e.output
        if not is_json(output):
            if len(output) > 0:
                logging.error('Speedtest CLI Error occurred that' +
                              'was not in JSON format')
            return (0, 0, 0, 0, 0, 0)
    except subprocess.TimeoutExpired:
        logging.error('Speedtest CLI process took too long to complete ' +
                      'and was killed.')
        return (0, 0, 0, 0, 0, 0)

    if is_json(output):
        data = json.loads(output)
        if "error" in data:
            # Socket error
            print('Something went wrong')
            print(data['error'])
            return (0, 0, 0, 0, 0, 0)  # Return all data as 0
        if "type" in data:
            if data['type'] == 'log':
                print(str(data["timestamp"]) + " - " + str(data["message"]))
            if data['type'] == 'result':
                actual_server = int(data['server']['id'])
                actual_jitter = data['ping']['jitter']
                actual_ping = data['ping']['latency']
                download = bytes_to_bits(data['download']['bandwidth'])
                upload = bytes_to_bits(data['upload']['bandwidth'])
                return (actual_server, actual_jitter, actual_ping, download,
                        upload, 1)


@app.route("/metrics")
def updateResults():
    global cache_until

    if datetime.datetime.now() > cache_until:
        r_server, r_jitter, r_ping, r_download, r_upload, r_status = runTest()
        server.set(r_server)
        jitter.set(r_jitter)
        ping.set(r_ping)
        download_speed.set(r_download)
        upload_speed.set(r_upload)
        up.set(r_status)
        logging.info("Server=" + str(r_server) + " Jitter=" + str(r_jitter) +
                     "ms" + " Ping=" + str(r_ping) + "ms" + " Download=" +
                     bits_to_megabits(r_download) + " Upload=" +
                     bits_to_megabits(r_upload))

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
