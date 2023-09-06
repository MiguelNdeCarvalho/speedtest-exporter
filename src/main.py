#!python

import logging
import os
import shutil
import subprocess

from flask import Flask
import prometheus_client as prometheus
from waitress import serve
from werkzeug.middleware import dispatcher

import exporter

# Setup logging values
format_string = 'level=%(levelname)s datetime=%(asctime)s %(message)s'
logging.basicConfig(encoding='utf-8',
                    level=logging.DEBUG,
                    format=format_string)

# Disable Waitress Logs
log = logging.getLogger('waitress')
# log.disabled = True


app = Flask("Speedtest-Exporter")  # Create flask app
app.wsgi_app = dispatcher.DispatcherMiddleware(
    app.wsgi_app,
    {
        '/metrics': prometheus.make_wsgi_app(),
    },
)


EXPORTER = exporter.SpeedtestExporter(
    cache_seconds=int(os.environ.get('SPEEDTEST_CACHE_FOR', 0)),
    server_id=os.environ.get('SPEEDTEST_SERVER'),
    timeout=int(os.environ.get('SPEEDTEST_TIMEOUT', 90)),
)


prometheus.REGISTRY.register(EXPORTER)


@app.route("/")
def mainPage():
    return ("<h1>Welcome to Speedtest-Exporter.</h1>" +
            "Click <a href='/metrics'>here</a> to see metrics.\n")


@app.route("/clear-cache", methods=['POST'])
def clear_cache():
    EXPORTER.clear()
    return "OK\n"


def checkForBinary():
    if shutil.which("speedtest") is None:
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
