from dataclasses import dataclass
from enum import Enum
from detaf.phenomenon import Phenomenon


class Proximity(str, Enum):
    VICINITY = "VC"


class Intensity(str, Enum):
    LIGHT = "-"
    HEAVY = "+"
    MODERATE = ""


class Descriptor(str, Enum):
    PATCHES = "BC"
    BLOWING = "BL"
    LOW_DRIFTING = "DR"
    FREEZING = "FZ"
    SHALLOW = "MI"
    PARTIAL = "PR"
    SHOWER = "SH"
    THUNDERSTORM = "TS"


class Precipitation(str, Enum):
    DRIZZLE = "DZ"
    HAIL = "GR"
    SMALL_HAIL = "GS"
    ICE_CRYSTALS = "IC"
    ICE_PELLETS = "PL"
    RAIN = "RA"
    SNOW_GRAINS = "SG"
    SNOW = "SN"
    UNKNOWN_PRECIPITATION = "UP"


class Obscuration(str, Enum):
    MIST = "BR"
    WIDESPREAD_DUST = "DU"
    FOG = "FG"
    SMOKE = "FU"
    HAZE = "HZ"
    SAND = "SA"
    VOLCANIC_ASH = "VA"


class Other(str, Enum):
    DUSTSTORM = "DS"
    FUNNEL_CLOUD = "FC"
    SAND_WHIRLS = "PO"
    SQUALLS = "SQ"
    SANDSTORM = "SS"


@dataclass
class Weather(Phenomenon):
    proximity: Proximity | None = None
    intensity: Intensity | None = None
    descriptor: Descriptor | None = None
    precipitation: Precipitation | None = None
    obscuration: Obscuration | None = None
    other: Other | None = None

    @property
    def category(self):
        return "weather"

    def taf_encode(self):
        parts = []
        if self.proximity:
            parts.append(self.proximity.value)
        if self.intensity:
            parts.append(self.intensity.value)
        if self.descriptor:
            parts.append(self.descriptor.value)
        if self.precipitation:
            parts.append(self.precipitation.value)
        if self.obscuration:
            parts.append(self.obscuration.value)
        if self.other:
            parts.append(self.other.value)
        return "".join(parts)

    @classmethod
    def taf_decode(cls, token: str):
        return parse(token)


def parse(token: str) -> Weather | None:
    index = 0

    # Proximity
    proximity = None
    for key in Proximity:
        if token[index:].startswith(key):
            proximity = key
            index += len(key)
            break

    # Intensity
    intensity = None
    for key in Intensity:
        if token[index:].startswith(key):
            intensity = key
            index += len(key)
            break

    # Descriptor
    descriptor = None
    for key in Descriptor:
        if token[index:].startswith(key):
            descriptor = key
            index += len(key)
            break

    # Precipitation
    precipitation = None
    for key in Precipitation:
        if token[index:].startswith(key):
            precipitation = key
            index += len(key)
            break

    # Obscuration
    obscuration = None
    for key in Obscuration:
        if token[index:].startswith(key):
            obscuration = key
            index += len(key)
            break

    # Other
    other = None
    for key in Other:
        if token[index:].startswith(key):
            other = key
            index += len(key)
            break

    if (precipitation is not None) or (obscuration is not None) or (other is not None):
        return Weather(
            proximity=proximity,
            intensity=intensity,
            descriptor=descriptor,
            precipitation=precipitation,
            obscuration=obscuration,
            other=other,
        )
    else:
        return None


decode = parse
