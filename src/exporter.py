import subprocess
import json
import datetime
import time
from prometheus_client import start_http_server, Gauge

def bytes_to_bits(bytes_per_sec):
    return bytes_per_sec * 8

def bits_to_megabits(bits_per_sec):
    megabits = round(bits_per_sec * (10**-6),2)
    return str(megabits) + "Mb/s"

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
        actual_ping = int(data['ping']['latency'])
        download = bytes_to_bits(data['download']['bandwidth'])
        upload = bytes_to_bits(data['upload']['bandwidth'])
        return (actual_ping, download, upload)

def update_results(test_done):
    ping.set(test_done[0])
    download_speed.set(test_done[1])
    upload_speed.set(test_done[2])
    current_dt = datetime.datetime.now()
    print(current_dt.strftime("%d/%m/%Y %H:%M:%S - ") + "Ping:" + str(test_done[0]) + " Download:" + bits_to_megabits(test_done[1]) + " Upload:" + bits_to_megabits(test_done[2]))

def run(http_port, sleep_time):
    start_http_server(http_port)
    print("Successfully started Speedtest Exporter on http://localhost:" + str(http_port))
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
