import pytest
import json


@pytest.fixture
def raw_pin_data():
    return {
        "title": "title",
        "description": "description",
        "dominant_color": "#ffffff",
        "hashtags": ["hashtags"],
        "images": {"736x": {"url": "img.jpg"}},
        "carousel_data": {},
    }

@pytest.fixture
def pin_html(raw_pin_data):
    html_script_data = {"props": {"initialReduxState": {"resources": {
        "PinResource": {"_": {"data": raw_pin_data}}
    }}}}

    html_script_data_json_string = json.dumps(html_script_data)

    html_script = f"""
        <script id='__PWS_DATA__' type='application/json'>
            {html_script_data_json_string}
        </script>
    """
    return html_script

