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
    def test_is_stored(self, mocker):
        mocker.patch("os.path.exists", return_value=True)
        data = '{"id": "1"}\n'
        mocker.patch("builtins.open", mocker.mock_open(read_data=data))

        storage = file.JsonStorage("filename")
        assert storage.is_stored("1")
        assert not storage.is_stored("2")

    def test_insert_pin(self, mocker):
        json_file = mocker.patch("builtins.open").return_value.__enter__.return_value
        dumps = mocker.patch("json.dumps", return_value="")

        new_data = {
            "id": "123",
            "url": "/pin/123",
            "title": "t",
            "description": "d",
            "dominant_color": "#ff00ff",
            "hashtags": ["#a"],
            "images": ["img.png"],
        }

        storage = file.JsonStorage("filename")
        storage.insert_pin(**new_data)

        dumps.assert_called_with(new_data)
        json_file.write.assert_called_with(dumps.return_value + "\n")
