import detaf
import pytest
from hypothesis import given
from hypothesis.strategies import text, sampled_from, integers, from_regex


# WEATHER


@given(
    intensity=sampled_from(detaf.weather.Intensity),
    descriptor=sampled_from(detaf.weather.Descriptor),
    precipitation=sampled_from(detaf.weather.Precipitation),
)
def test_decode_weather_given_intensity_descriptor_precipitation(
    intensity, descriptor, precipitation
):
    report = intensity + descriptor + precipitation
    assert detaf.weather.decode(report).intensity == intensity
    assert detaf.weather.decode(report).descriptor == descriptor
    assert detaf.weather.decode(report).precipitation == precipitation


@given(
    intensity=sampled_from(detaf.weather.Intensity),
    precipitation=sampled_from(detaf.weather.Precipitation),
)
def test_decode_weather_given_intensity_and_precipitation(intensity, precipitation):
    report = intensity + precipitation
    assert detaf.weather.decode(report).intensity == intensity
    assert detaf.weather.decode(report).precipitation == precipitation


@given(
    proximity=sampled_from(detaf.weather.Proximity),
    precipitation=sampled_from(detaf.weather.Precipitation),
)
def test_decode_weather_given_proximity_and_precipitation(proximity, precipitation):
    report = proximity + precipitation
    assert detaf.weather.decode(report).proximity == proximity
    assert detaf.weather.decode(report).precipitation == precipitation


@given(
    precipitation=sampled_from(detaf.weather.Precipitation),
)
def test_decode_weather_given_precipitation(precipitation):
    report = precipitation
    assert detaf.weather.decode(report).precipitation == precipitation


@given(
    obscuration=sampled_from(detaf.weather.Obscuration),
)
def test_decode_weather_given_obscuration(obscuration):
    report = obscuration
    assert detaf.weather.decode(report).obscuration == obscuration


@given(
    other=sampled_from(detaf.weather.Other),
)
def test_decode_weather_given_other(other):
    report = other
    assert detaf.weather.decode(report).other == other


# VISIBILITY


@given(distance=integers(min_value=0, max_value=9999))
def test_visibility(distance):
    report = f"TAF AAAA 000000Z 0000/0000 {distance:04}"
    assert detaf.decode(report).weather_conditions[0].phenomena[0].distance == distance


# WIND


@given(
    direction=integers(min_value=0, max_value=360),
    speed=integers(min_value=0, max_value=99),
)
def test_wind_direction_and_speed(direction, speed):
    report = f"TAF AAAA 000000Z 0000/0000 {direction:03}{speed:02}KT"
    wind = detaf.decode(report).weather_conditions[0].phenomena[0]
    assert wind.speed == speed
    assert wind.direction == direction


@given(
    direction=integers(min_value=0, max_value=360),
    speed=integers(min_value=0, max_value=99),
    gust=integers(min_value=0, max_value=99),
)
def test_wind_direction_speed_gust(direction, speed, gust):
    report = f"TAF AAAA 000000Z 0000/0000 {direction:03}{speed:02}G{gust:02}KT"
    wind = detaf.decode(report).weather_conditions[0].phenomena[0]
    assert wind.speed == speed
    assert wind.direction == direction
    assert wind.gust == gust


# Encode


@given(
    modification=sampled_from(detaf.Modification),
    icao_identifier=text("ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=4, max_size=4),
)
def test_encode_decoded_report(modification, icao_identifier):
    report = f"TAF"
    report += f" {modification.value}"
    report += f" {icao_identifier}"
    report += " 000000Z 0000/0000 9999 PROB30 TEMPO 0000/0000 9999 FM000000 5000"
    assert detaf.encode(detaf.decode(report)) == report


# CLOUD
@pytest.mark.parametrize("report", ["BKN008", "CAVOK", "SCT018CB", "FEW030TCU"])
def test_encode_decode_cloud(report):
    assert detaf.encode(detaf.cloud.decode(report)) == report


# Temperature
@pytest.mark.parametrize("report", ["TX27/1815Z", "TN15/1806Z"])
def test_encode_decode_temperature(report):
    assert detaf.encode(detaf.temperature.decode(report)) == report


def test_encode_decode():
    assert detaf.encode(detaf.decode("")) == ""


# FMDDHHMM syntax


@given(
    day=integers(min_value=0, max_value=31),
    hour=integers(min_value=0, max_value=31),
    minute=integers(min_value=0, max_value=31),
)
def test_fm_syntax(day, hour, minute):
    text = f"FM{day:02}{hour:02}{minute:02}"
    assert detaf.From.taf_decode(text).day == day
    assert detaf.From.taf_decode(text).hour == hour
    assert detaf.From.taf_decode(text).minute == minute


def test_fm_syntax_given_invalid_text():
    assert detaf.From.taf_decode("XX000000") is None


@given(
    day=integers(min_value=0, max_value=31),
    hour=integers(min_value=0, max_value=31),
    minute=integers(min_value=0, max_value=31),
)
def test_fm_encode(day, hour, minute):
    assert (
        detaf.From(day, hour, minute).taf_encode() == f"FM{day:02}{hour:02}{minute:02}"
    )


# METAR


@pytest.mark.parametrize(
    "report",
    [
        "METAR",
        "METAR EIDW",
        "METAR EIDW 010000Z",
        "METAR EIDW 010000Z 9999",
        "METAR EIDW 010000Z Q1024",
        "METAR EIDW 010000Z 11/05",
    ],
)
def test_metar_decode_encode_returns_same_string(report):
    assert detaf.encode(detaf.decode(report)) == report
