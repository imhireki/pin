from data.storage import file


class TestCSVStorage:
    def test_query_pin(self, mocker):
        mocker.patch('os.path.exists')
        stored_data = {"url": "my_pin_url"}
        mocker.patch('csv.reader', return_value=[stored_data])

        storage = file.CSVStorage('_')

        assert storage.query_pin(stored_data['url']) == stored_data['url']

    def test_insert_pin(self, mocker):
        csv_writer_mock = mocker.patch('csv.writer')
        new_pin_data = {"url": "my_pin_url"}

        storage = file.CSVStorage('_')
        storage.insert_pin(new_pin_data)

        assert csv_writer_mock.return_value.writerow.call_args.args == (new_pin_data,)

