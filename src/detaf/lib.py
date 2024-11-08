from dataclasses import dataclass, field
from enum import Enum
from collections import namedtuple


class Change(str, Enum):
    BECMG = "BECMG"
    TEMPO = "TEMPO"


class Version(str, Enum):
    ORIGINAL = "ORIGINAL"
    AMMENDED = "AMMENDED"
    CORRECTED = "CORRECTED"


class UnknownFormat(Exception):
    pass


issue = namedtuple("issue", "day hour minute")
period = namedtuple("period", "begin end")
dayhour = namedtuple("dayhour", "day hour")


@dataclass
class WeatherCondition:
    period: period
    probability: int | None = None
    change: Change | None = None


@dataclass
class TAF:
    version: str = Version
    icao_identifier: str | None = None
    issue_time: str = None
    weather_conditions: list[WeatherCondition] = field(default_factory=list)


def parse(bulletin: str) -> TAF:
    words = bulletin.strip().split(" ")
    words = [word.strip() for word in words if word != ""]
    print(words)

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
        return WeatherCondition(period, probability, change), cursor
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


def peek(tokens, cursor):
    try:
        return tokens[cursor]
    except IndexError:
        return None
