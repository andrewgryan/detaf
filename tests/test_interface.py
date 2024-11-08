import pytest
import detaf


def test_integration():
    report = """
    TAF EGAA 081058Z 0812/0912 14010KT 9999 BKN015
    TEMPO 0812/0906 6000 BKN008
    PROB30 TEMPO 0906/0912 BKN008
    """
    actual = detaf.parse(report)
    expected = detaf.TAF()
    assert actual == expected


@pytest.mark.parametrize("bulletin,expected", [
    ("TAF", detaf.Version.ORIGINAL),
    ("TAF AMD", detaf.Version.AMMENDED),
    ("TAF COR", detaf.Version.CORRECTED)
])
def test_parse_version(bulletin, expected):
    taf = detaf.parse(bulletin)
    assert isinstance(taf, detaf.TAF)
    assert taf.version == expected


@pytest.mark.parametrize("bulletin,expected", [
    ("TAF", None),
    ("TAF EIDW", "EIDW"),
    ("TAF AMD LFPG", "LFPG"),
])
def test_parse_icao_code(bulletin, expected):
    taf = detaf.parse(bulletin)
    assert taf.icao_identifier == expected


@pytest.mark.parametrize("bulletin,expected", [
    ("TAF LFPG 080500Z", (8, 5, 0)),
])
def test_parse_issue_time(bulletin, expected):
    taf = detaf.parse(bulletin)
    assert taf.issue_time == expected


@pytest.mark.parametrize("bulletin,expected", [
    ("TAF LFPG 080500Z", []),
    ("TAF LFPG 080500Z 0805/0905", [detaf.WeatherCondition(((8, 5), (9, 5)))]),
    ("TAF EIDW 080500Z 0805/0905 0807/0809", [
        detaf.WeatherCondition(detaf.period((8, 5), (9, 5))),
        detaf.WeatherCondition(detaf.period((8, 7), (8, 9))),
    ]),
    ("TAF EIDW 080500Z 0805/0905 PROB30 TEMPO 0807/0809", [
        detaf.WeatherCondition(detaf.period((8, 5), (9, 5))),
        detaf.WeatherCondition(detaf.period((8, 7), (8, 9)), probability=30, change=detaf.Change.TEMPO),
    ]),
    ("TAF EIDW 080500Z 0805/0905 TEMPO 0807/0809", [
        detaf.WeatherCondition(detaf.period((8, 5), (9, 5))),
        detaf.WeatherCondition(detaf.period((8, 7), (8, 9)), change=detaf.Change.TEMPO),
    ]),
    ("TAF EIDW 080500Z 0805/0905 BECMG 0807/0809", [
        detaf.WeatherCondition(detaf.period((8, 5), (9, 5))),
        detaf.WeatherCondition(detaf.period((8, 7), (8, 9)), change=detaf.Change.BECMG),
    ])
])
def test_parse_weather_conditions(bulletin, expected):
    taf = detaf.parse(bulletin)
    assert taf.weather_conditions == expected
