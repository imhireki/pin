from storage import file


class TestCSVStorage:
    def test_query_pin(self, mocker, pin_data):
        mocker.patch("csv.reader", return_value=[list(pin_data.values())])
        mocker.patch("os.path.exists")
        mocker.patch("builtins.open")

        storage = file.CSVStorage("filename")
        query_pin_result = storage.query_pin(pin_data["url"])

        assert query_pin_result == pin_data["url"]

    def test_insert_pin(self, mocker, pin_data):
        csv_writer_mock = mocker.patch("csv.writer")
        mocker.patch("builtins.open")

        storage = file.CSVStorage("filename")
        storage.insert_pin(pin_data)

        assert csv_writer_mock.return_value.writerow.call_args.args[0] == list(
            pin_data.values()
        )


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
