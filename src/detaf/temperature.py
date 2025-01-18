from enum import Enum
from collections import namedtuple
from dataclasses import dataclass


@dataclass
class TemperatureDewPoint:
    """METAR temperature/dew point encoder"""

    temperature: int
    dew_point: int

    @classmethod
    def taf_decode(cls, report: str):
        if "/" in report:
            return cls(
                temperature=cls._int(report[0:2]), dew_point=cls._int(report[3:5])
            )

    def taf_encode(self) -> str:
        return f"{self._str(self.temperature)}/{self._str(self.dew_point)}"

    @staticmethod
    def _str(n):
        if n < 0:
            return f"M{abs(n)}"
        else:
            return f"{n:02d}"

    @staticmethod
    def _int(s):
        if s[0] == "M":
            return -1 * int(s[1:])
        else:
            return int(s)


class Limit(str, Enum):
    MIN = "N"
    MAX = "X"


dayhour = namedtuple("dayhour", "day hour")


@dataclass
class Temperature:
    value: int
    limit: Limit
    at: dayhour

    @staticmethod
    def taf_decode(token: str):
        if token.startswith("TX") or token.startswith("TN"):
            value = int(token[2:4])
            limit = token[1]
            at = dayhour(int(token[5:7]), int(token[7:9]))
            return Temperature(value, limit, at)
        else:
            return None

    def taf_encode(self):
        return f"T{self.limit}{self.value:02}/{self.at.day:02}{self.at.hour:02}Z"


def decode(s: str):
    return Temperature.taf_decode(s)
