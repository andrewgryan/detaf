import detaf
from jinja2 import Environment


def test_html_templating():
    report = "TAF ABCD 000000Z 0000/0000 +RA CAVOK VRB01KT 0001/0002 4000"
    env = Environment()
    env.filters["encode"] = detaf.encode
    template = env.from_string("""
    <div>
        <span class="format">{{ taf.format | encode }}</span>
        <span class="icao">{{ taf.icao_identifier }}</span>
        <span class="issue">{{ taf.issue_time | encode }}</span>
        {%- for condition in taf.weather_conditions %}
        <span class="period">{{ condition.period | encode }}</span>
        {%- for phenomenon in condition.phenomena %}
            {% if phenomenon.category == "visibility" -%}
            <span class="vis">{{ phenomenon | encode }}</span>
            {%- elif phenomenon.category == "weather" -%}
            <span class="precip">{{ phenomenon | encode }}</span>
            {%- elif phenomenon.category == "wind" -%}
            <span class="wind">{{ phenomenon | encode }}</span>
            {%- elif phenomenon.category == "cloud" -%}
            <span class="cloud">{{ phenomenon | encode }}</span>
            {%- else -%}
            <span class="raw">{{ phenomenon | encode }}</span>
            {%- endif %}
        {%- endfor %}
        {%- endfor %}
    </div>
    """)
    expect = """
    <div>
        <span class="format">TAF</span>
        <span class="icao">ABCD</span>
        <span class="issue">000000Z</span>
        <span class="period">0000/0000</span>
            <span class="precip">+RA</span>
            <span class="cloud">CAVOK</span>
            <span class="wind">VRB01KT</span>
        <span class="period">0001/0002</span>
            <span class="vis">4000</span>
    </div>
    """
    assert template.render(taf=detaf.decode(report)) == expect


def test_template_metar():
    report = "METAR EIDW 010000Z"
    env = Environment()
    env.filters["encode"] = detaf.encode
    template = env.from_string("""
        <h1>{{ tac.icao_identifier | encode }}</h1>
        <p>{{ tac.issue_time.day }}</p>
    """)
    expect = """
        <h1>EIDW</h1>
        <p>1</p>
    """
    assert template.render(tac=detaf.decode(report)) == expect
