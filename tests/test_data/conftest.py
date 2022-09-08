import json

import pytest


base_pin_data = {
    "title": "title",
    "description": "description",
    "dominant_color": "#ffffff",
    "hashtags": ['hashtag'],
}

@pytest.fixture
def pin_data():
    return {
        "url": "https://www.pinterest.com/pin/123/",
        "images": ['img.jpg'],
        **base_pin_data
    }

@pytest.fixture
def raw_pin_data():
    return {
        **base_pin_data,
        "carousel_data": {},
        "images": {"736x": {"url": "img.jpg"}}
    }

@pytest.fixture
def make_pin_html():
    def _make_pin_html(raw_pin_data):
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
    return _make_pin_html
