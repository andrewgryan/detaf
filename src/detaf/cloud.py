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


class Type(str, Enum):
    CUMULONIMBUS = "CB"
    TOWERING_CUMULONIMBUS = "TCU"


@dataclass
class Cloud:
    description: CloudDescription
    height: int | None = None
    type: Type | None = None

    def taf_encode(self):
        parts = [self.description.value]
        if self.height:
            h = self.height // 100  # integer divide
            parts.append(f"{h:03}")
        if self.type:
            parts.append(self.type.value)
        return "".join(parts)

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

        # Type
        type = None
        for key in Type:
            width = len(key)
            if token[pointer : pointer + width] == key:
                type = key
                pointer += width

        if description:
            return Cloud(description, height, type)
        else:
            return None


def decode(text):
    return Cloud.taf_decode(text)
