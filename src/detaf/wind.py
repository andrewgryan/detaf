from dataclasses import dataclass
from detaf.phenomenon import Phenomenon


@dataclass
class Wind(Phenomenon):
    direction: int | str
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
