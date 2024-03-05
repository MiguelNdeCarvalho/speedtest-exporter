#!/bin/bash
set -e

docker build -t speedtest-img .

docker run -dit --name speedtest-claro -p 9798:9798 -e SPEEDTEST_SERVER=28385 \
           -e SPEEDTEST_PORT=9798 -e SPEEDTEST_LOG_LEVEL=debug speedtest-img

docker run -dit --name speedtest-vivo -p 9799:9799 -e SPEEDTEST_SERVER=21537 \
           -e SPEEDTEST_PORT=9799 -e SPEEDTEST_LOG_LEVEL=debug speedtest-img

docker ps
