import speedtest
import datetime

def btomb(speed):
    speed = speed * pow(10,-6)
    return speed

servers = []
s = speedtest.Speedtest()
s.get_servers(servers)
s.get_best_server()
down_speed=s.download()
up_speed=s.upload()
currentDT = datetime.datetime.now()
print("Current Download Speed:" + str(btomb(down_speed)) + " at: " + currentDT.strftime("%H:%M:%S"))
print("Current Upload Speed:" + str(btomb(up_speed)) + " at: " + currentDT.strftime("%H:%M:%S"))