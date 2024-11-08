import pytest
import detaf


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
