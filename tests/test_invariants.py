import detaf
from hypothesis import given
from hypothesis.strategies import text, sampled_from


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
