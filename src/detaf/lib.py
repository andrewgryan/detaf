from dataclasses import dataclass
from enum import Enum


class Version(str, Enum):
    ORIGINAL = "ORIGINAL"
    AMMENDED = "AMMENDED"
    CORRECTED = "CORRECTED"


class UnknownFormat(Exception):
    pass


@dataclass
class TAF:
    version: str = Version
    icao_identifier: str | None = None
    issue_time: str = None


def parse(bulletin: str) -> TAF:
    words = bulletin.split(" ")

    format, cursor = parse_format(words, 0)
    version, cursor = parse_version(words, cursor)
    icao_identifier, cursor = parse_icao_identifier(words, cursor)
    issue_time, cursor = parse_issue_time(words, cursor)
    
    return TAF(version, icao_identifier, issue_time)


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


def parse_issue_time(tokens, cursor=0):
    return (8, 5, 0), cursor + 1


def peek(tokens, cursor):
    try:
        return tokens[cursor]
    except IndexError:
        return None
