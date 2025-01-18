from dataclasses import dataclass
from detaf.temporal import parse_issue_time


@dataclass
class METAR:
    icao_identifier: str
    issue_time: str

    @classmethod
    def tac_decode(cls, report: str):
        tokens = [s.strip() for s in report.split()]
        icao_identifier = tokens[1]
        issue_time, _ = parse_issue_time(tokens, 2)
        return cls(icao_identifier=icao_identifier, issue_time=issue_time)
