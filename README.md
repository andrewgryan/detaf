# Decode TAF
[![tests](https://img.shields.io/github/actions/workflow/status/andrewgryan/detaf/test.yml?branch=main&logo=github&style=for-the-badge)](https://github.com/andrewgryan/detaf/actions/workflows/test.yml)
![License](https://img.shields.io/github/license/andrewgryan/detaf?style=for-the-badge)


![463267a9-1d75-4edf-b8e0-38b98977111b~3.jpg](https://github.com/user-attachments/assets/d4b3808a-550d-440e-96a1-a5286ef33767)

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

# Render encoded sections and information

Detaf enables partial encoding,
to make it easier to annotate parts of the report.
For example, to add tooltips or syntax highlighting.

The encoder `detaf.encode` is polymorphic,
to make it easier to selectively render TAF snippets or Python data.

```python
>>> import detaf
>>> bulletin = """TAF EIDW 081700Z 0818/0918 14010KT 4000 -DZ BKN007
... BECMG 0818/0820 9999 NSW SCT010 BKN015
... BECMG 0901/0903 15005KT
... BECMG 0907/0909 13010KT
... TEMPO 0907/0918 BKN012
... PROB30 TEMPO 0907/0912 4000 -DZ BKN008"""
>>> taf = detaf.decode(bulletin)
>>>
>>> html = ""
>>> for cnd in taf.weather_conditions:
...     html += f"<div>{detaf.encode(cnd)}</div>\n"
...
>>> print(html)
<div>0818/0918 14010KT 4000 -DZ BKN007</div>
<div>BECMG 0818/0820 9999 NSW SCT010 BKN015</div>
<div>BECMG 0901/0903 15005KT</div>
<div>BECMG 0907/0909 13010KT</div>
<div>TEMPO 0907/0918 BKN012</div>
<div>TEMPO PROB30 0907/0912 4000 -DZ BKN008</div>
```

Or a single weather condition list of weather phenomena.

```python
>>> for ph in taf.weather_conditions[1].phenomena:
...     print(f"<li>{detaf.encode(ph)}</li>")
...
<li>9999</li>
<li>NSW</li>
<li>SCT010</li>
<li>BKN015</li>
```

The ability to map back and forth from a data structure to TAF encoding allows hypermedia driven applications to interpret TAF reports.
