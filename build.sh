#!/bin/bash
set -e

docker build -t speedtest-img .

docker run -dit --name speedtest-claro -p 9798:9798 -e SPEEDTEST_SERVER=12561 \
           -e SPEEDTEST_PORT=9798 -e SPEEDTEST_LOG_LEVEL=debug -e SPEEDTEST_CACHE_FOR=300 speedtest-img

docker run -dit --name speedtest-vivo -p 9799:9799 -e SPEEDTEST_SERVER=21836 \
           -e SPEEDTEST_PORT=9799 -e SPEEDTEST_LOG_LEVEL=debug -e SPEEDTEST_CACHE_FOR=300 speedtest-img

docker ps