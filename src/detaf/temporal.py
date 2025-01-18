"""
TAC specific date and time data structures
"""

from detaf.parser import peek
from collections import namedtuple

issue = namedtuple("issue", "day hour minute")


def parse_issue_time(tokens, cursor=0):
    token = peek(tokens, cursor)
    if not token:
        return None, cursor

    # Parse ddhhMMZ format into tuple
    day = int(token[:2])
    hour = int(token[2:4])
    minute = int(token[4:6])
    return issue(day, hour, minute), cursor + 1


def encode_issue_time(value):
    return f"{value.day:02}{value.hour:02}{value.minute:02}Z"
