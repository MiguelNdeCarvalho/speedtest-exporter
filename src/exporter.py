import subprocess
import json
import os
import logging
import datetime
from prometheus_client import make_wsgi_app, Gauge, Info
from flask import Flask
from waitress import serve
from shutil import which

app = Flask("Speedtest-Exporter")  # Create flask app

# Setup logging values
log_level_conf = {'debug': logging.DEBUG, 'info': logging.INFO,
                  'warning': logging.WARNING, 'error': logging.ERROR}
LOG_LEVEL = os.getenv('SPEEDTEST_LOG_LEVEL', 'info')
format_string = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(encoding='utf-8', 
                    level=log_level_conf.get(LOG_LEVEL),
                    format=format_string)

# Disable Waitress Logs
log = logging.getLogger('waitress')
log.disabled = True

# Cache metrics for how long (seconds)?
cache_seconds = int(os.environ.get('SPEEDTEST_CACHE_FOR', 0))
cache_until = datetime.datetime.fromtimestamp(0)

# Create Metrics
jitter = Gauge('speedtest_jitter_latency_milliseconds',
               'Speedtest current Jitter in ms')
ping = Gauge('speedtest_ping_latency_milliseconds',
             'Speedtest current Ping in ms')
download_speed = Gauge('speedtest_download_bits_per_second',
                       'Speedtest current Download Speed in bit/s')
upload_speed = Gauge('speedtest_upload_bits_per_second',
                     'Speedtest current Upload speed in bits/s')
packet_loss = Gauge('speedtest_packet_loss',
                    'Speedtest current Packet Loss in %')
up = Gauge('speedtest_up', 'Speedtest status whether the scrape worked')
info = Info('speedtest', 'Speedtest test informations')


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
    timeout = int(os.environ.get('SPEEDTEST_TIMEOUT', 90))

    cmd = [
        "speedtest", "--format=json-pretty", "--progress=no",
        "--accept-license", "--accept-gdpr"
    ]
    if serverID:
        cmd.append(f"--server-id={serverID}")
    try:
        logging.debug(cmd)
        output = subprocess.check_output(cmd, timeout=timeout)
    except subprocess.CalledProcessError as e:
        output = e.output
        if not is_json(output):
            if len(output) > 0:
                logging.error('Speedtest CLI Error occurred that' +
                              'was not in JSON format')
            return (0, '', '', '', '', '', 0, 0, 0, 0, 0, '', 0)
    except subprocess.TimeoutExpired:
        logging.error('Speedtest CLI process took too long to complete ' +
                      'and was killed.')
        return (0, '', '', '', '', '', 0, 0, 0, 0, 0, '', 0)

    if is_json(output):
        data = json.loads(output)
        logging.debug(data)
        if "error" in data:
            # Socket error
            logging.error('Something went wrong')
            logging.error(data['error'])
            return (0, '', '', '', '', '', 0, 0, 0, 0, 0, '', 0)
        if "type" in data:
            if data['type'] == 'log':
                logging.info(str(data["message"]))
            if data['type'] == 'result':
                actual_server_id = int(data['server']['id'])
                actual_server_name = data['server']['name']
                actual_server_host = data['server']['host']
                actual_server_location = data['server']['location']
                actual_server_country = data['server']['country']
                actual_server_ip = data['server']['ip']
                actual_jitter = data['ping']['jitter']
                actual_ping = data['ping']['latency']
                actual_download = bytes_to_bits(data['download']['bandwidth'])
                actual_upload = bytes_to_bits(data['upload']['bandwidth'])
                actual_loss = data.get('packetLoss', '0')
                actual_isp = data.get('isp')

                return (actual_server_id, actual_server_name, actual_server_host, 
                        actual_server_location, actual_server_country, actual_server_ip,
                        actual_jitter, actual_ping, actual_download, actual_upload, 
                        actual_loss, actual_isp, 1)


@app.route("/metrics")
def updateResults():
    global cache_until

    if datetime.datetime.now() > cache_until:
        r_server_id, r_server_name, r_server_host, r_server_location, r_server_country, r_server_ip, r_jitter, r_ping, r_download, r_upload, r_loss, r_isp, r_status = runTest()
        
        jitter.set(r_jitter)
        ping.set(r_ping)
        download_speed.set(r_download)
        upload_speed.set(r_upload)
        packet_loss.set(r_loss)
        up.set(r_status)
        info.info({'server_id' : str(r_server_id), 'server_name' : r_server_name, 
                   'server_host' : r_server_host, 'server_location' : r_server_location, 
                   'server_country' : r_server_country, 'server_ip' : r_server_ip,
                   'isp' : r_isp})

        logging.info("Server=" + str(r_server_name) + " (" + str(r_server_id) + ")" +
                     " ISP=" + str(r_isp) + " Jitter=" + str(r_jitter) + "ms" + 
                     " Ping=" + str(r_ping) + "ms" + " PacketLoss=" + str(r_loss) +
                     " Download=" + bits_to_megabits(r_download) + " Upload=" + bits_to_megabits(r_upload))

        cache_until = datetime.datetime.now() + datetime.timedelta(seconds=cache_seconds)
    else:
        logging.debug("Cached Until: " + str(cache_until))

    return make_wsgi_app()


@app.route('/health', methods=['GET'])
def health():
    return "Healthy: OK"


@app.route("/")
def mainPage():
    return ("<h1>Welcome to Speedtest-Exporter.</h1>" +
            "Click <a href='/metrics'>here</a> to see metrics.<br>" +
            "Click <a href='/health'>here</a> to see healthy.")


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
    
    logging.debug("SPEEDTEST_PORT: " + str(os.getenv('SPEEDTEST_PORT')))
    logging.debug("SPEEDTEST_SERVER: " + str(os.getenv('SPEEDTEST_SERVER')))
    logging.debug("SPEEDTEST_TIMEOUT: " + str(os.getenv('SPEEDTEST_TIMEOUT')))
    logging.debug("SPEEDTEST_CACHE_FOR: " + str(os.getenv('SPEEDTEST_CACHE_FOR')))
    logging.debug("SPEEDTEST_LOG_LEVEL: " + str(os.getenv('SPEEDTEST_LOG_LEVEL')))

    serve(app, host='0.0.0.0', port=PORT)