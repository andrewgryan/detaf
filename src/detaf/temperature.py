from enum import Enum
from collections import namedtuple
from dataclasses import dataclass


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
