import subprocess
import json
import os
from prometheus_client import make_wsgi_app, Gauge
from flask import Flask
from waitress import serve
import logging

app = Flask("Speedtest-Exporter")  # Create flask app

# Create Metrics
labels = ["server_id"]

jitter = Gauge('speedtest_jitter_latency_milliseconds', 'Speedtest current Jitter in ms', labels)
ping = Gauge('speedtest_ping_latency_milliseconds', 'Speedtest current Ping in ms', labels)
download_speed = Gauge('speedtest_download_bits_per_second', 'Speedtest current Download Speed in bit/s', labels)
upload_speed = Gauge('speedtest_upload_bits_per_second', 'Speedtest current Upload speed in bits/s', labels)
packet_loss = Gauge('speedtest_packet_loss', 'Speedtest current Packet Loss in %', labels)
up = Gauge('speedtest_up', 'Speedtest status whether the scrape worked', labels)


def bytes_to_bits(bytes_per_sec):
    return bytes_per_sec * 8


def bits_to_megabits(bits_per_sec):
    megabits = round(bits_per_sec * (10**-6), 2)
    return str(megabits) + " Mb/s"


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def runTest():
    serverID = os.environ.get('SPEEDTEST_SERVER')
    timeout = int(os.environ.get('SPEEDTEST_TIMEOUT', 90))

    cmd = ["speedtest", "--format=json-pretty", "--progress=no",
           "--accept-license", "--accept-gdpr"]
    if serverID:
        cmd.append(f"--server-id={serverID}")

    try:
        log.debug(cmd)
        output = subprocess.check_output(cmd, timeout=timeout)

    except subprocess.CalledProcessError as e:
        output = e.output
        if not is_json(output):
            if len(output) > 0:
                log.error('Speedtest CLI Error occurred that was not in JSON format')
                log.error(output)
            return (0, 0, 0, 0, 0, 0)

    except subprocess.TimeoutExpired:
        log.error('Speedtest CLI process took too long to complete and was killed.')
        return (0, 0, 0, 0, 0, 0)

    if is_json(output):
        data = json.loads(output)
        log.debug(data)
        if "error" in data:
            # Socket error
            log.error('Something went wrong')
            log.error(data['error'])
            return (0, 0, 0, 0, 0, 0)  # Return all data as 0
        if "type" in data:
            if data['type'] == 'log':
                log.info(str(data["message"]))
            if data['type'] == 'result':
                actual_server = data.get('server')
                actual_jitter = data['ping']['jitter']
                actual_ping = data['ping']['latency']
                download = bytes_to_bits(data['download']['bandwidth'])
                upload = bytes_to_bits(data['upload']['bandwidth'])
                loss = data.get('packetLoss', '0')

                return (actual_server, actual_jitter,
                        actual_ping, download, upload, loss, 1)


@app.route("/metrics")
def updateResults():
    r_server, r_jitter, r_ping, r_download, r_upload, r_loss, r_status = runTest()

    jitter.labels(server_id=r_server['id']).set(r_jitter)
    ping.labels(server_id=r_server['id']).set(r_ping)
    download_speed.labels(server_id=r_server['id']).set(r_download)
    upload_speed.labels(server_id=r_server['id']).set(r_upload)
    packet_loss.labels(server_id=r_server['id']).set(r_loss)
    up.labels(server_id=r_server['id']).set(r_status)

    log.info("Server: " + str(r_server['id']) + " | Jitter: " + str(r_jitter)
             + " ms | Ping: " + str(r_ping) + " ms | Download: "
             + bits_to_megabits(r_download) + " | Upload:" + bits_to_megabits(r_upload)
             + " | Packet Loss: " + str(r_loss))

    return make_wsgi_app()


@app.route('/health', methods=['GET'])
def health():
    return "Healthy: OK"


@app.route("/")
def mainPage():
    return ("<h1>Welcome to Speedtest-Exporter.</h1>" +
            "Click <a href='/metrics'>here</a> to see metrics.<br>" +
            "Click <a href='/health'>here</a> to see healthy.")


if __name__ == '__main__':

    # Log Config
    log_level_conf = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR}
    LOG_LEVEL = os.getenv('SPEEDTEST_LOG_LEVEL', 'info')

    global log
    log = logging.getLogger("speedtest-exporter")
    log.setLevel(log_level_conf.get(LOG_LEVEL))
    log.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(handler)

    PORT = os.getenv('SPEEDTEST_PORT', 9798)
    print("Starting Speedtest-Exporter on http://localhost:" + str(PORT))
    serve(app, host='0.0.0.0', port=PORT)
