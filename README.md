# Decode TAF

Convert a TAF string

```python
>>> import detaf
>>> bulletin = """
... TAF EGAA 081058Z 0812/0912 14010KT 9999 BKN015
... TEMPO 0812/0906 6000 BKN008
... PROB30 TEMPO 0906/0912 BKN008
... """
>>> detaf.parse(bulletin)
... TAF(
...   version=<Version.ORIGINAL: 'ORIGINAL'>,
...   icao_identifier='EGAA',
...   issue_time=issue(day=8, hour=10, minute=58),
...   weather_conditions=[
...     WeatherCondition(period=period(begin=dayhour(day=8, hour=12), end=dayhour(day=9, hour=12)), probability=None, change=None),
...     WeatherCondition(period=period(begin=dayhour(day=8, hour=12), end=dayhour(day=9, hour=6)), probability=None, change=None),
...     WeatherCondition(period=period(begin=dayhour(day=9, hour=6), end=dayhour(day=9, hour=12)), probability=None, change=<Change.TEMPO: 'TEMPO'>)
...   ])

```
