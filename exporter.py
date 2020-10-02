import datetime
import time
import speedtest
from prometheus_client import start_http_server, Summary, Gauge

def btomb(speed):
    speed = speed * pow(10,-6)
    return speed

ping = Gauge('speedtest_ping', 'Speedtest current Ping')
download_speed = Gauge('speedtest_download_speed', 'Speedtest current Download Speed')
upload_speed = Gauge('speedtest_upload_speed', 'Upload speed')

def test():
    servers = []
    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    current_ping=s.results.ping
    down_speed=s.download()
    up_speed=s.upload()
    currentDT = datetime.datetime.now()
    print("Current Download Speed:" + str(btomb(down_speed)) + " at: " + currentDT.strftime("%H:%M:%S"))
    print("Current Upload Speed:" + str(btomb(up_speed)) + " at: " + currentDT.strftime("%H:%M:%S"))
    ping.set(current_ping)
    download_speed.set(down_speed)
    upload_speed.set(up_speed)
    time.sleep(95)

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        test()
