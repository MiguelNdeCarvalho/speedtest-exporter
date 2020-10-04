import subprocess
import json
import datetime
import time
from prometheus_client import start_http_server, Gauge

def to_mb(bytes_per_sec):
    mbs=round(bytes_per_sec / (10**6), 2)
    return str(mbs) + " MB/s"

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

def run_speedtest():
    cmd = ["speedtest", "--format=json-pretty", "--progress=no", "--accept-license", "--accept-gdpr"]
    output = subprocess.check_output(cmd)
    if is_json(output):
        data = json.loads(output)
        actual_ping = int(float(data['ping']['latency']))
        download = to_mb(data['download']['bandwidth'])
        upload = to_mb(data['upload']['bandwidth'])
        return (actual_ping, download, upload)

def update_results(test_done):
    ping.set(test_done[0])
    download_speed.set(test_done[1])
    upload_speed.set(test_done[2])
    current_dt = datetime.datetime.now()
    print(current_dt.strftime("%H:%M:%S -") + "Ping:" + str(test_done[0]) + " Download:" + to_mb(test_done[1]) + " Upload:" + to_mb(test_done[2]))

def run(http_port, sleep_time):
    start_http_server(http_port)
    print("Sucessfully started Speedtest Exporter on http://localhost:" + str(http_port))
    while True:
        test = run_speedtest()
        update_results(test)
        time.sleep(sleep_time)

if __name__ == '__main__':
    # Create the Metrics
    ping = Gauge('speedtest_ping', 'Speedtest current Ping')
    download_speed = Gauge('speedtest_download_speed', 'Speedtest current Download Speed')
    upload_speed = Gauge('speedtest_upload_speed', 'Upload speed')
    PORT=9112
    SLEEP=95
    run(PORT, SLEEP)
