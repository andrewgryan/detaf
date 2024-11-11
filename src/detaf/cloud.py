from dataclasses import dataclass
from enum import Enum


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
        if self.height:
            h = self.height // 100  # integer divide
            return f"{self.description.value}{h:03}"
        else:
            return self.description.value

    @staticmethod
    def taf_decode(token: str):
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
            return Cloud(description, height)
        else:
            return None


def decode(text):
    return Cloud.taf_decode(text)
