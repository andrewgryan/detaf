from dataclasses import dataclass
from enum import Enum


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
class Wx:
    proximity: Proximity | None = None
    intensity: Intensity | None = None
    descriptor: Descriptor | None = None
    precipitation: Precipitation | None = None
    obscuration: Obscuration | None = None
    other: Other | None = None


def parse(token: str) -> Wx | None:
    index = 0

    # Intensity
    intensity = None
    for key in Intensity:
        if token[index:].startswith(key):
            intensity = key
            index += len(key)
            break

    # Precipitation
    precipitation = None
    for key in Precipitation:
        if token[index:].startswith(key):
            precipitation = key
            index += len(key)
            break

    if precipitation is None:
        return None
    else:
        return Wx(intensity=intensity, precipitation=precipitation)
