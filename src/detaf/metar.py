from dataclasses import dataclass
from detaf.temporal import issue, parse_issue_time, encode_issue_time
from detaf.phenomenon import phenomena_parser
from detaf.cloud import Cloud
from detaf.visibility import Visibility
from detaf.wind import Wind


@dataclass
class METAR:
    icao_identifier: str
    issue_time: issue
    phenomena: list[str]

    @classmethod
    def tac_decode(cls, report: str):
        """Construct METAR from TAC encoded string"""
        tokens = [s.strip() for s in report.split()]
        try:
            icao_identifier = tokens[1]
        except IndexError:
            icao_identifier = ""
        issue_time, cursor = parse_issue_time(tokens, 2)
        phenomena, _ = phenomena_parser([Wind, Visibility, Cloud])(tokens, cursor)
        return cls(icao_identifier=icao_identifier, issue_time=issue_time, phenomena=phenomena)

    def taf_encode(self) -> str:
        # TODO: deprecate taf_encode method
        return self.tac_encode()

    def tac_encode(self) -> str:
        parts = ["METAR"]
        if self.icao_identifier:
            parts.append(self.icao_identifier)
        if self.issue_time:
            parts.append(encode_issue_time(self.issue_time))
        return " ".join(parts)
