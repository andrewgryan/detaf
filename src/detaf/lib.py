import re
from dataclasses import dataclass, field
from enum import Enum
from collections import namedtuple
from detaf import wx, temperature
from detaf.cloud import Cloud
from detaf.temperature import Temperature
from detaf import wx as weather


class Change(str, Enum):
    BECMG = "BECMG"
    TEMPO = "TEMPO"


@dataclass
class From:
    """Forecast condition change after certain time"""

    day: int
    hour: int
    minute: int

    @staticmethod
    def taf_decode(text: str):
        if text[:2] == "FM":
            day = int(text[2:4])
            hour = int(text[4:6])
            minute = int(text[6:8])
            return From(day, hour, minute)

    def taf_encode(self) -> str:
        return f"FM{self.day:02}{self.hour:02}{self.minute:02}"


class Modification(str, Enum):
    AMMENDED = "AMD"
    CORRECTED = "COR"


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

    @staticmethod
    def taf_decode(token: str):
        if token.endswith("KT"):
            if "G" in token:
                gust = int(token[6:8])
            else:
                gust = None
            direction = None
            try:
                direction = int(token[:3])
            except ValueError:
                direction = token[:3]
                assert direction == "VRB", "must be either VRB or 3-digit number"
            return Wind(direction, int(token[3:5]), gust)
        else:
            return None  # Explicit is better than implicit


class Wx(str, Enum):
    NO_SIGNIFICANT_WEATHER = "NSW"

    def taf_encode(self):
        return "NSW"


Phenomenon = Visibility | Wind | Cloud


@dataclass
class WeatherCondition:
    period: period = None
    probability: int | None = None
    change: Change | None = None
    fm: From | None = None
    phenomena: list[Phenomenon] = field(default_factory=list)

    def taf_encode(self):
        parts = []
        if self.probability:
            parts.append(f"PROB{self.probability:02}")
        if self.change:
            parts.append(self.change.value)
        if self.period:
            parts.append(encode_period(self.period))
        for phenomenon in self.phenomena:
            parts.append(phenomenon.taf_encode())
        return " ".join(parts)


class Format(str, Enum):
    TAF = "TAF"
    # METAR = "METAR"
    # SPECI = "SPECI"


@dataclass
class TAF:
    format: Format | None = Format.TAF
    modification: Modification | None = None
    icao_identifier: str | None = None
    issue_time: str = None
    weather_conditions: list[WeatherCondition] = field(default_factory=list)

    def __iter__(self):
        if self.format:
            yield self.format
        if self.modification:
            yield self.modification
        if self.icao_identifier:
            yield self.icao_identifier
        if self.issue_time:
            yield self.issue_time
        yield from self.weather_conditions

    def taf_encode(self) -> str:
        return " ".join(encode(item) for item in self)


def parse(bulletin: str) -> TAF:
    words = bulletin.strip().split()
    words = [word.strip() for word in words if word != ""]

    # Station information and bulletin time
    format, cursor = parse_format(words, 0)
    modification, cursor = parse_modification(words, cursor)
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

    return TAF(format, modification, icao_identifier, issue_time, conditions)


def parse_format(tokens, cursor=0):
    token = peek(tokens, cursor)
    for key in Format:
        if token == key:
            return key, cursor + 1
    return None, cursor


def parse_modification(tokens, cursor=0) -> (Modification | None, int):
    token = peek(tokens, cursor)
    for key in Modification:
        if token == key:
            return key, cursor + 1
    return None, cursor


def parse_icao_identifier(tokens, cursor=0):
    icao_identifier = peek(tokens, cursor)
    if icao_identifier:
        return icao_identifier, cursor + 1
    else:
        return None, cursor


def parse_condition(tokens, cursor=0):
    probability, cursor = parse_probability(tokens, cursor)
    fm, cursor = parse_decoder(From.taf_decode)(tokens, cursor)
    if fm:
        phenomena, cursor = parse_phenomena(tokens, cursor)
        return WeatherCondition(
            fm=fm, probability=probability, phenomena=phenomena
        ), cursor
    else:
        change, cursor = parse_change(tokens, cursor)
        period, cursor = parse_period(tokens, cursor)
        phenomena, cursor = parse_phenomena(tokens, cursor)
        if period:
            return WeatherCondition(
                period, probability, change, phenomena=phenomena
            ), cursor
    return None, cursor


def parse_phenomena(tokens, cursor):
    phenomena = []
    while cursor < len(tokens):
        phenomenon, cursor = parse_phenomenon(tokens, cursor)
        if phenomenon:
            phenomena.append(phenomenon)
        else:
            break
    return phenomena, cursor


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
    for parser in [
        parse_visibility,
        parse_wind,
        parse_cloud,
        parse_nsw,
        parse_wx,
        parse_t,
    ]:
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


def parse_decoder(decoder):
    def parser(tokens, cursor=0):
        token = peek(tokens, cursor)
        obj = decoder(token)
        if obj:
            return obj, cursor + 1
        else:
            return None, cursor

    return parser


def parse_wind(tokens, cursor=0):
    token = peek(tokens, cursor)
    wind = Wind.taf_decode(token)
    if wind:
        return wind, cursor + 1
    else:
        return None, cursor


def parse_cloud(tokens, cursor=0):
    token = peek(tokens, cursor)
    obj = Cloud.taf_decode(token)
    if obj:
        return obj, cursor + 1
    else:
        return None, cursor


def parse_t(tokens, cursor=0):
    token = peek(tokens, cursor)
    obj = Temperature.taf_decode(token)
    if obj:
        return obj, cursor + 1
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
    elif isinstance(item, str):
        return item
    else:
        return item.taf_encode()


def encode_issue_time(value):
    return f"{value.day:02}{value.hour:02}{value.minute:02}Z"


def encode_period(value):
    return f"{value.begin.day:02}{value.begin.hour:02}/{value.end.day:02}{value.end.hour:02}"
