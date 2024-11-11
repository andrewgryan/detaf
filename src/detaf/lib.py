import re
from dataclasses import dataclass, field
from enum import Enum
from collections import namedtuple
from detaf import wx
from detaf import wx as weather


class Change(str, Enum):
    BECMG = "BECMG"
    TEMPO = "TEMPO"


class Version(str, Enum):
    ORIGINAL = "ORIGINAL"
    AMMENDED = "AMD"
    CORRECTED = "COR"

    def taf_encode(self) -> str:
        if self == Version.ORIGINAL:
            return ""
        else:
            return self.value


class UnknownFormat(Exception):
    pass


issue = namedtuple("issue", "day hour minute")
period = namedtuple("period", "begin end")
dayhour = namedtuple("dayhour", "day hour")


@dataclass
class Visibility:
    distance: int

    def taf_encode(self):
        return f"{self.distance}"


@dataclass
class Wind:
    direction: int
    speed: int
    gust: int | None = None

    def taf_encode(self):
        if self.gust:
            return f"{self.direction:03}{self.speed:02}G{self.gust:02}KT"
        else:
            return f"{self.direction:03}{self.speed:02}KT"


class CloudDescription(str, Enum):
    NO_SIGNIFICANT_CLOUD = "NSC"
    CEILING_AND_VISIBILITY_OK = "CAVOK"
    FEW = "FEW"
    BROKEN = "BKN"
    OVERCAST = "OVC"
    SCATTERED = "SCT"
    SKY_CLEAR = "SKC"


@dataclass
class Cloud:
    description: CloudDescription
    height: int

    def taf_encode(self):
        return f"{self.description.value}{self.height}"


class Wx(str, Enum):
    NO_SIGNIFICANT_WEATHER = "NSW"

    def taf_encode(self):
        return "NSW"


Phenomenon = Visibility | Wind | Cloud


@dataclass
class WeatherCondition:
    period: period
    probability: int | None = None
    change: Change | None = None
    phenomena: list[Phenomenon] = field(default_factory=list)

    def taf_encode(self):
        parts = [
            encode_period(self.period)
        ]
        if self.probability:
            parts.insert(0, f"PROB{self.probability:02}")
        if self.change:
            parts.insert(0, self.change.value)
        for phenomenon in self.phenomena:
            parts.append(phenomenon.taf_encode())
        return " ".join(parts)


@dataclass
class TAF:
    version: str = Version
    icao_identifier: str | None = None
    issue_time: str = None
    weather_conditions: list[WeatherCondition] = field(default_factory=list)

    def taf_encode(self) -> str:
        parts = ["TAF"]
        if self.version != Version.ORIGINAL:
            parts.append(self.version.taf_encode())
        if self.icao_identifier:
            parts.append(self.icao_identifier)
        if self.issue_time:
            parts.append(encode_issue_time(self.issue_time))
        for weather in self.weather_conditions:
            parts.append(weather.taf_encode())
        return " ".join(parts)


def parse(bulletin: str) -> TAF:
    words = bulletin.strip().split()
    words = [word.strip() for word in words if word != ""]

    # Station information and bulletin time
    format, cursor = parse_format(words, 0)
    version, cursor = parse_version(words, cursor)
    icao_identifier, cursor = parse_icao_identifier(words, cursor)
    issue_time, cursor = parse_issue_time(words, cursor)

    # Weather condition(s)
    conditions = []
    while cursor < len(words):
        condition, cursor = parse_condition(words, cursor)
        if condition:
            conditions.append(condition)
        else:
            print(f"unrecognised token: {words[cursor]}")
            cursor += 1  # Skip: bad token
    
    return TAF(version, icao_identifier, issue_time, conditions)


def parse_format(tokens, cursor=0):
    token = peek(tokens, cursor)
    if token == "TAF":
        return TAF, cursor + 1
    else:
        raise UnknownFormat(token)
        

def parse_version(tokens, cursor=0) -> (Version, int):
    token = peek(tokens, cursor)
    if token == "AMD":
        return Version.AMMENDED, cursor + 1
    elif token == "COR":
        return Version.CORRECTED, cursor + 1
    else:
        return Version.ORIGINAL, cursor


def parse_icao_identifier(tokens, cursor=0):
    icao_identifier = peek(tokens, cursor)
    if icao_identifier:
        return icao_identifier, cursor + 1
    else:
        return None, cursor


def parse_condition(tokens, cursor=0):
    probability, cursor = parse_probability(tokens, cursor)
    change, cursor = parse_change(tokens, cursor)
    period, cursor = parse_period(tokens, cursor)
    if period:
        phenomena = []
        while cursor < len(tokens):
            phenomenon, cursor = parse_phenomenon(tokens, cursor)
            if phenomenon:
                phenomena.append(phenomenon)
            else:
                break
        return WeatherCondition(period, probability, change, phenomena=phenomena), cursor
    else:
        return None, cursor


def parse_issue_time(tokens, cursor=0):
    token = peek(tokens, cursor)
    if not token:
        return None, cursor

    # Parse ddhhMMZ format into tuple
    day = int(token[:2])
    hour = int(token[2:4])
    minute = int(token[4:6])
    return issue(day, hour, minute), cursor + 1



def parse_period(tokens, cursor=0):
    token = peek(tokens, cursor)
    if not token:
        return None, cursor
    if not is_period(token):
        return None, cursor

    # Parse ddhh/ddhh format into period
    begin = dayhour(int(token[0:2]), int(token[2:4]))
    end = dayhour(int(token[5:7]), int(token[7:9]))
    return period(begin, end), cursor + 1


def is_period(token):
    return (len(token) == 9) and (token[4] == "/")


def parse_probability(tokens, cursor=0):
    token = peek(tokens, cursor)
    if token.startswith("PROB"):
        return int(token[4:6]), cursor + 1
    else:
        return None, cursor


def parse_change(tokens, cursor=0):
    token = peek(tokens, cursor)
    if token == "TEMPO":
        return Change.TEMPO, cursor + 1
    elif token == "BECMG":
        return Change.BECMG, cursor + 1
    else:
        return None, cursor


def parse_phenomenon(tokens, cursor=0):
    for parser in [parse_visibility, parse_wind, parse_cloud, parse_nsw, parse_wx]:
        phenomenon, cursor = parser(tokens, cursor)
        if phenomenon:
            return phenomenon, cursor
    return None, cursor

    
def parse_visibility(tokens, cursor=0):
    pattern = re.compile(r"[0-9]{4}")
    token = peek(tokens, cursor)
    if len(token) == 4 and pattern.match(token):
        return Visibility(int(token)), cursor + 1
    else:
        return None, cursor


def parse_wind(tokens, cursor=0):
    token = peek(tokens, cursor)
    if token.endswith("KT"):
        if "G" in token:
            gust = int(token[6:8])
        else:
            gust = None
        return Wind(int(token[:3]), int(token[3:5]), gust), cursor + 1
    else:
        return None, cursor


def parse_cloud(tokens, cursor=0):
    token = peek(tokens, cursor)

    # Description
    pointer = 0
    description = None
    for key in CloudDescription:
        if token.startswith(key):
            description = key
            pointer += len(key)
            break

    # Height
    height = None
    try:
        width = 3
        height = 100 * int(token[pointer : pointer + width])
        pointer += width
    except ValueError:
        pass

    if description:
        return Cloud(description, height), cursor + 1
    else:
        return None, cursor


def parse_nsw(tokens, cursor=0):
    token = peek(tokens, cursor)
    if token == Wx.NO_SIGNIFICANT_WEATHER:
        return Wx.NO_SIGNIFICANT_WEATHER, cursor + 1
    else:
        return None, cursor


def parse_wx(tokens, cursor=0):
    token = peek(tokens, cursor)
    obj = wx.parse(token)
    if obj:
        return obj, cursor + 1
    else:
        return None, cursor


def peek(tokens, cursor):
    try:
        return tokens[cursor]
    except IndexError:
        return None


decode = parse


def encode(item) -> str:
    if isinstance(item, issue):
        return encode_issue_time(item)
    elif isinstance(item, period):
        return encode_period(item)
    else:
        return item.taf_encode()


def encode_issue_time(value):
    return f"{value.day:02}{value.hour:02}{value.minute:02}Z"


def encode_period(value):
    return f"{value.begin.day:02}{value.begin.hour:02}/{value.end.day:02}{value.end.hour:02}"
