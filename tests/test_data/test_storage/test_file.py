from data.storage import file


class TestCSVStorage:
    def test_query_pin(self, mocker):
        mocker.patch('os.path.exists')
        stored_data = {"url": "my_pin_url"}
        mocker.patch('csv.reader', return_value=[list(stored_data.values())])

        storage = file.CSVStorage('_')

        assert storage.query_pin(stored_data['url']) == stored_data['url']

    def test_insert_pin(self, mocker):
        csv_writer_mock = mocker.patch('csv.writer')
        new_pin_data = {"url": "my_pin_url"}

        storage = file.CSVStorage('_')
        storage.insert_pin(new_pin_data)

        assert csv_writer_mock.return_value.writerow.call_args.args == (
            list(new_pin_data.values()),
        )


class TestJsonStorage:
    def test_query_pin(self, mocker):
        stored_data = {"url": "my_pin_url"}

        storage = file.JsonStorage('_')
        get_json_data_mock = mocker.patch.object(
            storage, '_get_json_data', return_value=[stored_data]
        )

        assert storage.query_pin(stored_data['url']) == stored_data['url']

    def test_insert_pin(self, mocker):
        json_dump_mock = mocker.patch('json.dump')
        stored_data = {"url": "pin_123"}
        new_pin_data = {"url": "my_pin_url"}

        storage = file.JsonStorage('_')
        get_json_data_mock = mocker.patch.object(
            storage, '_get_json_data', return_value=[stored_data]
        )

        storage.insert_pin(new_pin_data)

        assert [stored_data, new_pin_data] in json_dump_mock.call_args.args

