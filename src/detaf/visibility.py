import re
from dataclasses import dataclass
from detaf.phenomenon import Phenomenon



@dataclass
class Visibility(Phenomenon):
    distance: int

    def taf_encode(self):
        return f"{self.distance}"

    @staticmethod
    def taf_decode(token: str):
        pattern = re.compile(r"[0-9]{4}")
        if len(token) == 4 and pattern.match(token):
            return Visibility(int(token))
        else:
            return None
