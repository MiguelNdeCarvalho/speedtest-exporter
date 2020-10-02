import datetime
import time
import speedtest
from prometheus_client import start_http_server, Gauge

def btomb(speed):
    speed = speed * pow(10,-6)
    return speed

def run_speedtest():
    servers = []
    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    actual_ping=s.results.ping
    download=s.download()
    upload=s.upload()
    return (actual_ping, download, upload)

def update_results(test_done):
    ping.set(test_done[0])
    download_speed.set(test_done[1])
    upload_speed.set(test_done[2])

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
