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
def test_decode_weather_given_intensity_descriptor_precipitation(intensity, descriptor, precipitation):
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
    speed=integers(min_value=0, max_value=99)
)
def test_wind_direction_and_speed(direction, speed):
    report = f"TAF AAAA 000000Z 0000/0000 {direction:03}{speed:02}KT"
    wind = detaf.decode(report).weather_conditions[0].phenomena[0]
    assert wind.speed == speed
    assert wind.direction == direction

@given(
    direction=integers(min_value=0, max_value=360),
    speed=integers(min_value=0, max_value=99),
    gust=integers(min_value=0, max_value=99)
)
def test_wind_direction_speed_gust(direction, speed, gust):
    report = f"TAF AAAA 000000Z 0000/0000 {direction:03}{speed:02}G{gust:02}KT"
    wind = detaf.decode(report).weather_conditions[0].phenomena[0]
    assert wind.speed == speed
    assert wind.direction == direction
    assert wind.gust == gust


# Encode

@given(
    version=sampled_from(detaf.Version),
    icao_identifier=text("ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=4, max_size=4),
)
def test_encode_decoded_report(version, icao_identifier):
    report = f"TAF"
    if version != detaf.Version.ORIGINAL:
        report += f" {version.value}"
    report += f" {icao_identifier}"
    report += " 000000Z"
    assert detaf.encode(detaf.decode(report)) == report


# CLOUD
@pytest.mark.parametrize("report", [
    "BKN008",
    "CAVOK"
])
def test_encode_decode_cloud(report):
    assert detaf.encode(detaf.cloud.decode(report)) == report
