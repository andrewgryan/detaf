import pytest
import detaf
from detaf import wx


def test_integration():
    report = """
    TAF EGAA 081058Z 0812/0912 14010KT 9999 BKN015
    TEMPO 0812/0906 6000 BKN008
    PROB30 TEMPO 0906/0912 BKN008
    """
    actual = detaf.decode(report)
    expected = detaf.TAF(
        icao_identifier="EGAA",
        issue_time=detaf.issue(8, 10, 58),
        weather_conditions=[
            detaf.WeatherCondition(
                period=((8, 12), (9, 12)),
                phenomena=[
                    detaf.Wind(140, 10),
                    detaf.Visibility(9999),
                    detaf.Cloud("BKN", 1500),
                ],
            ),
            detaf.WeatherCondition(
                period=((8, 12), (9, 6)),
                change=detaf.Change.TEMPO,
                phenomena=[detaf.Visibility(6000), detaf.Cloud("BKN", 800)],
            ),
            detaf.WeatherCondition(
                period=((9, 6), (9, 12)),
                probability=30,
                change=detaf.Change.TEMPO,
                phenomena=[detaf.Cloud("BKN", 800)],
            ),
        ],
    )
    assert actual == expected


def test_integration_eigw():
    report = """
    TAF EIDW 081700Z 0818/0918 14010KT 4000 -DZ BKN007
    BECMG 0818/0820 9999 NSW SCT010 BKN015
    BECMG 0901/0903 15005KT
    BECMG 0907/0909 13010KT
    TEMPO 0907/0918 BKN012
    PROB30 TEMPO 0907/0912 4000 -DZ BKN008
    """
    actual = detaf.decode(report)
    expected = detaf.TAF(
        icao_identifier="EIDW",
        issue_time=detaf.issue(8, 17, 0),
        weather_conditions=[
            # 0818/0918 14010KT 4000 -DZ BKN007
            detaf.WeatherCondition(
                period=((8, 18), (9, 18)),
                phenomena=[
                    detaf.Wind(140, 10),
                    detaf.Visibility(4000),
                    detaf.Weather(intensity="-", precipitation="DZ"),
                    detaf.Cloud("BKN", 700),
                ],
            ),
            # BECMG 0818/0820 9999 NSW SCT010 BKN015
            detaf.WeatherCondition(
                period=((8, 18), (8, 20)),
                change=detaf.Change.BECMG,
                phenomena=[
                    detaf.Visibility(9999),
                    detaf.NSW.NO_SIGNIFICANT_WEATHER,
                    detaf.Cloud("SCT", 1000),
                    detaf.Cloud("BKN", 1500),
                ],
            ),
            # BECMG 0901/0903 15005KT
            detaf.WeatherCondition(
                period=((9, 1), (9, 3)),
                change=detaf.Change.BECMG,
                phenomena=[
                    detaf.Wind(150, 5),
                ],
            ),
            # BECMG 0907/0909 13010KT
            detaf.WeatherCondition(
                period=((9, 7), (9, 9)),
                change=detaf.Change.BECMG,
                phenomena=[
                    detaf.Wind(130, 10),
                ],
            ),
            # TEMPO 0907/0918 BKN012
            detaf.WeatherCondition(
                period=((9, 7), (9, 18)),
                change=detaf.Change.TEMPO,
                phenomena=[detaf.Cloud("BKN", 1200)],
            ),
            # PROB30 TEMPO 0907/0912 4000 -DZ BKN008
            detaf.WeatherCondition(
                period=((9, 7), (9, 12)),
                change=detaf.Change.TEMPO,
                probability=30,
                phenomena=[
                    detaf.Visibility(4000),
                    detaf.Weather(intensity="-", precipitation="DZ"),
                    detaf.Cloud("BKN", 800),
                ],
            ),
        ],
    )
    assert actual == expected


def test_integration_from():
    report = """
    TAF EIDW 081700Z 0818/0918 14010KT 4000 -DZ BKN007
    FM090100 15005KT
    TEMPO 0907/0918 BKN012
    PROB30 TEMPO 0907/0912 4000 -DZ BKN008
    """
    actual = detaf.decode(report).weather_conditions[1]
    expected = detaf.WeatherCondition(
        fm=detaf.From(9, 1, 0), phenomena=[detaf.Wind(direction=150, speed=5)]
    )
    assert actual == expected


@pytest.mark.parametrize(
    "bulletin,expected",
    [
        ("TAF", None),
        ("TAF AMD", detaf.Modification.AMMENDED),
        ("TAF COR", detaf.Modification.CORRECTED),
    ],
)
def test_parse_version(bulletin, expected):
    taf = detaf.decode(bulletin)
    assert isinstance(taf, detaf.TAF)
    assert taf.modification == expected


@pytest.mark.parametrize(
    "bulletin,expected",
    [
        ("TAF", None),
        ("TAF EIDW", "EIDW"),
        ("TAF AMD LFPG", "LFPG"),
    ],
)
def test_parse_icao_code(bulletin, expected):
    taf = detaf.decode(bulletin)
    assert taf.icao_identifier == expected


@pytest.mark.parametrize(
    "bulletin,expected",
    [
        ("TAF LFPG 080500Z", (8, 5, 0)),
    ],
)
def test_parse_issue_time(bulletin, expected):
    taf = detaf.decode(bulletin)
    assert taf.issue_time == expected


@pytest.mark.parametrize(
    "bulletin,expected",
    [
        ("TAF LFPG 080500Z", []),
        ("TAF LFPG 080500Z 0805/0905", [detaf.WeatherCondition(((8, 5), (9, 5)))]),
        (
            "TAF EIDW 080500Z 0805/0905 0807/0809",
            [
                detaf.WeatherCondition(detaf.period((8, 5), (9, 5))),
                detaf.WeatherCondition(detaf.period((8, 7), (8, 9))),
            ],
        ),
        (
            "TAF EIDW 080500Z 0805/0905 PROB30 TEMPO 0807/0809",
            [
                detaf.WeatherCondition(detaf.period((8, 5), (9, 5))),
                detaf.WeatherCondition(
                    detaf.period((8, 7), (8, 9)),
                    probability=30,
                    change=detaf.Change.TEMPO,
                ),
            ],
        ),
        (
            "TAF EIDW 080500Z 0805/0905 TEMPO 0807/0809",
            [
                detaf.WeatherCondition(detaf.period((8, 5), (9, 5))),
                detaf.WeatherCondition(
                    detaf.period((8, 7), (8, 9)), change=detaf.Change.TEMPO
                ),
            ],
        ),
        (
            "TAF EIDW 080500Z 0805/0905 BECMG 0807/0809",
            [
                detaf.WeatherCondition(detaf.period((8, 5), (9, 5))),
                detaf.WeatherCondition(
                    detaf.period((8, 7), (8, 9)), change=detaf.Change.BECMG
                ),
            ],
        ),
    ],
)
def test_parse_weather_conditions(bulletin, expected):
    taf = detaf.decode(bulletin)
    assert taf.weather_conditions == expected


@pytest.mark.parametrize(
    "bulletin,expected",
    [
        ("TAF EIDW 081647Z 0816/0916 9999", [detaf.Visibility(9999)]),
        (
            "TAF EIDW 081647Z 0816/0916 TX27/1815Z",
            [detaf.Temperature(27, "X", at=(18, 15))],
        ),
        (
            "TAF EIDW 081647Z 0816/0916 TN15/1806Z",
            [detaf.Temperature(15, "N", at=(18, 6))],
        ),
    ],
)
def test_parse_visibility(bulletin, expected):
    taf = detaf.decode(bulletin)
    assert taf.weather_conditions[0].phenomena == expected


def test_parse_wx():
    assert wx.decode("-DZ") == wx.Weather(
        intensity=wx.Intensity.LIGHT, precipitation=wx.Precipitation.DRIZZLE
    )


def test_iterable():
    assert list(detaf.decode("TAF COR")) == ["TAF", detaf.Modification.CORRECTED]


def test_variable_wind_conditions():
    text = "VRB02KT"
    assert detaf.Wind.taf_decode(text).direction == "VRB"
    assert detaf.Wind.taf_decode(text).speed == 2
    assert detaf.Wind.taf_decode(text).taf_encode() == text


def test_preserve_unknown_text():
    report = "TAF ABCD 000000Z 0000/0000 FOO 0000/0000 BAR"
    assert detaf.encode(detaf.decode(report)) == report
