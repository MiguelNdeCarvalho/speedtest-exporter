# Speedtest Exporter

Simple **Speedtest exporter** for **Prometheus** written in **Python** using the
official CLI from **Ookla**

You can get all the documentation [here](https://docs.miguelndecarvalho.pt/projects/speedtest-exporter/)

## Environment variables

| Environment Var     | Default | Description                                                                                                                     |
| ------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------- |
| SPEEDTEST_CACHE_FOR | 0       | Cache results for _x_ seconds                                                                                                   |
| SPEEDTEST_SERVER    | NA      | Speedtest server to use, if left unset Speedtest will choose one                                                                |
| SPEEDTEST_TIMEOUT   | 90      | How long to let the speed test run for before timeing out                                                                       |
| SPEEDTEST_DELAY     | 0       | Delay the starting of the Speedtest <br/>(useful if you are running multiple Speedtest exporters e.g. testing a VPN connection) |

## Thanks to

- [Nils Müller](https://github.com/tyriis)
