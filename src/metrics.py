#

from prometheus_client import core


def download_speed() -> core.GaugeMetricFamily:
    return core.GaugeMetricFamily(
        'speedtest_download_bits_per_second',
        'current download Speed in bit/s',
        labels=('result_uuid',),
    )


def jitter() -> core.GaugeMetricFamily:
    return core.GaugeMetricFamily(
        'speedtest_jitter_latency_milliseconds',
        'current jitter in ms',
        labels=('result_uuid',),
    )


def ping() -> core.GaugeMetricFamily:
    return core.GaugeMetricFamily(
        'speedtest_ping_latency_milliseconds',
        'current ping in ms',
        labels=('result_uuid',),
    )


def up() -> core.GaugeMetricFamily:
    return core.GaugeMetricFamily(
        'speedtest_up',
        '1 if the scrape worked, 0 otherwise',
    )


def upload_speed() -> core.GaugeMetricFamily:
    return core.GaugeMetricFamily(
        'speedtest_upload_bits_per_second',
        'current upload Speed in bit/s',
        labels=('result_uuid',),
    )
