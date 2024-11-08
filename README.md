# Decode TAF

Convert a TAF string to a data structure.

```python
>>> import detaf
>>> bulletin = """
... TAF EGAA 081058Z 0812/0912 14010KT 9999 BKN015
... TEMPO 0812/0906 6000 BKN008
... PROB30 TEMPO 0906/0912 BKN008
... """
>>> detaf.parse(bulletin)
TAF(
  version=<Version.ORIGINAL: 'ORIGINAL'>,
  icao_identifier='EGAA',
  issue_time=issue(day=8, hour=10, minute=58),
  weather_conditions=[
    WeatherCondition(
      period=period(begin=dayhour(day=8, hour=12), end=dayhour(day=9, hour=12)),
      probability=None,
      change=None,
      phenomena=[Wind(direction=140, speed=10, gust=None), Visibility(distance=9999)]),
      ...
```

Easy to traverse data structure, suitable for any template engine.

```python
>>> taf = detaf.parse(bulletin)
>>> for cnd in taf.weather_conditions:
...     for phenom in cnd.phenomena:
...         print(cnd.period, phenom)
...
period(begin=dayhour(day=8, hour=12), end=dayhour(day=9, hour=12)) Wind(direction=140, speed=10, gust=None)
period(begin=dayhour(day=8, hour=12), end=dayhour(day=9, hour=12)) Visibility(distance=9999)
period(begin=dayhour(day=8, hour=12), end=dayhour(day=9, hour=12)) Cloud(description=<CloudDescription.BROKEN: 'BKN'>, height=1500)
period(begin=dayhour(day=8, hour=12), end=dayhour(day=9, hour=6)) Visibility(distance=6000)
period(begin=dayhour(day=8, hour=12), end=dayhour(day=9, hour=6)) Cloud(description=<CloudDescription.BROKEN: 'BKN'>, height=800)
period(begin=dayhour(day=9, hour=6), end=dayhour(day=9, hour=12)) Cloud(description=<CloudDescription.BROKEN: 'BKN'>, height=800)
```
