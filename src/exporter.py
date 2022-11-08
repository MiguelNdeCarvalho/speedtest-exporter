#!python

import logging
import json
import subprocess
import typing

import prometheus_client as prometheus

import cache
import data
import metrics


def safe_json(payload) -> typing.Optional[dict]:
    try:
        return json.loads(payload)
    except ValueError:
        return None

    return None


def speedtest(
    server_id: str = '',
    timeout: int = 90,
) -> typing.Optional[data.SpeedtestResult]:
    cmd = [
        "speedtest",
        "--format=json",
        "--progress=no",
        "--accept-license",
        "--accept-gdpr",
    ]

    if server_id:
        cmd.append(f"--server-id={server_id}")

    try:
        output = subprocess.check_output(cmd, timeout=timeout)

    except subprocess.CalledProcessError as e:
        output = e.output
    except subprocess.TimeoutExpired:
        logging.error('Speedtest CLI process took too long to complete ' +
                      'and was killed.')
        return None

    result = safe_json(output)

    if not result:
        if len(output) > 0:
            logging.error('Speedtest CLI Error occurred that' +
                          'was not in JSON format')
        return None

    error = result.get('error')
    if error:
        # Socket error
        print(f'Something went wrong: {error}')
        return None

    result_type = result.get('type')

    if result_type == 'log':
        timestamp = result.get('timestamp')
        message = result.get('message')

        print(str(timestamp) + " - " + str(message))

        return None

    if result_type == 'result':
        return data.SpeedtestResult.parse(result)

    return None


class SpeedtestExporter:
    def __init__(
        self,
        cache_seconds: int = 0,
        server_id: str = '',
        timeout: int = 90,
    ):
        self._cache_seconds = cache_seconds
        self._server_id = server_id
        self._timeout = timeout

        self._speedtest = cache.ttl_cache(ttl=cache_seconds)(speedtest)
        self._speedtest = self.duration.time()(self._speedtest)

    duration = prometheus.Summary(
        'speedtest_duration_seconds',
        'duration in seconds',
    )

    def clear(self):
        self._speedtest.clear()

    def describe(self):
        yield metrics.download_speed()
        yield metrics.jitter()
        yield metrics.ping()
        yield metrics.up()
        yield metrics.upload_speed()

    def collect(self):
        result = None
        cached = self._speedtest.get(self._server_id, self._timeout)

        if not cached:
            result = self._speedtest(self._server_id, self._timeout)

        if result is None and cached is not None:
            result = cached.value

        download = metrics.download_speed()
        jitter = metrics.jitter()
        ping = metrics.ping()
        up = metrics.up()
        upload = metrics.upload_speed()

        emit = [
            download,
            jitter,
            ping,
            up,
            upload,
        ]

        if result is not None:
            labels = (result.result.id,)

            download.add_metric(labels, result.download.bps())
            jitter.add_metric(labels, result.ping.jitter)
            ping.add_metric(labels, result.ping.latency)
            upload.add_metric(labels, result.upload.bps())

        up.add_metric((), 1 if result is not None else 0)

        for metric in emit:
            yield metric
