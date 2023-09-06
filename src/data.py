#

import dataclasses
import datetime


@dataclasses.dataclass
class Interface:
    external_ip: str
    internal_ip: str
    is_vpn: bool
    mac_address: str
    name: str

    @classmethod
    def parse(cls, payload: dict) -> 'Interface':
        return cls(
            external_ip=payload.get('external_ip', ''),
            internal_ip=payload.get('internal_ip', ''),
            is_vpn=payload.get('is_vpn', False),
            mac_address=payload.get('mac_address', ''),
            name=payload.get('name', ''),
        )


@dataclasses.dataclass
class Latency:
    igm: float
    low: float
    high: float
    jitter: float

    @classmethod
    def parse(cls, payload: dict) -> 'Latency':
        return cls(
            igm=payload.get('igm', 0),
            low=payload.get('low', 0),
            high=payload.get('high', 0),
            jitter=payload.get('jitter', 0),
        )


@dataclasses.dataclass
class Ping:
    jitter: float
    latency: float
    low: float
    high: float

    @classmethod
    def parse(cls, payload: dict) -> 'Ping':
        return cls(
            jitter=payload.get('jitter', 0),
            latency=payload.get('latency', 0),
            low=payload.get('low', 0),
            high=payload.get('high', 0),
        )


@dataclasses.dataclass
class Result:
    id: str
    persisted: bool
    url: str

    @classmethod
    def parse(cls, payload: dict) -> 'Result':
        return cls(
            id=payload.get('id', ''),
            persisted=payload.get('persisted', False),
            url=payload.get('url', ''),
        )


@dataclasses.dataclass
class Speedtest:
    bandwidth: int
    bytes: int
    elapsed: int
    latency: float

    @classmethod
    def parse(cls, payload: dict) -> 'Speedtest':
        return cls(
            bandwidth=payload.get('bandwidth', 0),
            bytes=payload.get('bytes', 0),
            elapsed=payload.get('elapsed', 0),
            latency=payload.get('latency', 0),
        )

    def bps(self) -> int:
        return self.bandwidth * 8


@dataclasses.dataclass
class Server:
    id: int
    host: str
    port: int
    name: str
    location: str
    country: str
    ip: str

    @classmethod
    def parse(cls, payload: dict) -> 'Server':
        return cls(
            id=payload.get('id', 0),
            host=payload.get('host', ''),
            port=payload.get('port', 0),
            name=payload.get('name', ''),
            location=payload.get('location', ''),
            country=payload.get('country', ''),
            ip=payload.get('ip', ''),
        )


@dataclasses.dataclass
class SpeedtestResult:
    download: Speedtest
    interface: Interface
    isp: str
    packet_loss: float
    ping: Ping
    result: Result
    server: Server
    timestamp: datetime.datetime
    type: str
    upload: Speedtest

    @classmethod
    def parse(cls, payload: dict) -> 'SpeedtestResult':
        return cls(
            download=Speedtest.parse(payload.get('download', {})),
            interface=Interface.parse(payload.get('interface', {})),
            isp=payload.get('isp', ''),
            packet_loss=payload.get('packetLoss', 0),
            ping=Ping.parse(payload.get('ping', {})),
            result=Result.parse(payload.get('result', {})),
            server=Server.parse(payload.get('server', {})),
            timestamp=datetime.datetime.strptime(
                payload.get('timestamp', '1970-01-01T00:00:00Z'),
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            type=payload.get('type', ''),
            upload=Speedtest.parse(payload.get('upload', {})),
        )
