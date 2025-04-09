import pytest

from storage import file


class TestCSVStorage:
    @pytest.mark.parametrize(
        "pin_id, data, result",
        [
            ("123", ["123", "title"], True),
            ("123", ["2"], False),
        ],
    )
    def test_is_stored(self, mocker, pin_id, data, result):
        mocker.patch("os.path.exists")
        mocker.patch("builtins.open")
        mocker.patch("csv.reader", return_value=[data])

        storage = file.CSVStorage("filename")
        assert storage.is_stored(pin_id) == result

    def test_insert_pin(self, mocker):
        writer = mocker.patch("csv.writer").return_value
        mocker.patch("builtins.open")

        data = {
            "id": "123",
            "url": "/pin/123",
            "title": "t",
            "description": "d",
            "dominant_color": "#ff00ff",
            "hashtags": ["#a"],
            "images": ["img.png"],
        }

        storage = file.CSVStorage("filename")
        storage.insert_pin(**data)

        writer.writerow.assert_called_with(list(data.values()))


class TestJsonStorage:
    def test_query_pin(self, mocker, pin_data):
        mocker.patch("builtins.open")

        storage = file.JsonStorage("filename")
        mocker.patch.object(storage, "_get_json_data", return_value=[pin_data])
        query_pin_result = storage.query_pin(pin_data["url"])

        assert query_pin_result == pin_data["url"]

    def test_insert_pin(self, mocker, pin_data):
        mocker.patch("builtins.open")
        json_dump_mock = mocker.patch("json.dump")

        storage = file.JsonStorage("filename")
        mocker.patch.object(storage, "_get_json_data", return_value=[pin_data])
        storage.insert_pin(pin_data)

        assert [pin_data, pin_data] in json_dump_mock.call_args.args
