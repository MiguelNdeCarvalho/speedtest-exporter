#!/bin/bash
set -e

docker stop speedtest-vivo
docker stop speedtest-claro
docker rm speedtest-vivo
docker rm speedtest-claro
docker rmi speedtest-img