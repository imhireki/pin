from data.storage import database


def test_postgresql_connection(mocker):
    connect_mock = mocker.patch('psycopg.connect')
    connection_options = {"dbname": "dbname", "password": 123}
    connection = database.PostgreSQLConnection(**connection_options)

    connection.connect()
    connection.commit()
    connection.disconnect()
    cursor = connection.get_cursor()

    assert connect_mock.call_args.kwargs == connection_options
    assert connection.connection.commit.called
    assert connection.connection.close.called
    assert cursor == connection.connection.cursor.return_value

def test_mysql_connection(mocker):
    connect_mock = mocker.patch('mysql.connector.connect')
    connection_options = {"database": "database", "password": 123}
    connection = database.MySQLConnection(**connection_options)

    connection.connect()
    connection.commit()
    connection.disconnect()
    cursor = connection.get_cursor()

    assert connect_mock.call_args.kwargs == connection_options
    assert connection.connection.commit.called
    assert connection.connection.close.called
    assert cursor == connection.connection.cursor.return_value


class TestPostgreSQLStorage:
    def test_storage(self, mocker):
        connection_mock = mocker.patch('data.storage.database.PostgreSQLConnection')
        database_config = {"user": "u", "password": "pass", "host": "localhost"}

        database.PostgreSQLStorage(database="db", **database_config)

        assert connection_mock.call_args.kwargs == dict(dbname="db", **database_config)

    def test_query_pin(self, mocker):
        connection_mock = mocker.patch('data.storage.database.PostgreSQLConnection')
        stored_pin = 'https://www.pinterest.com/pin/123/'

        storage = database.PostgreSQLStorage(*[_ for _ in range(4)])
        select_from_mock = mocker.patch.object(
            storage, '_select_from',
            mocker.Mock(return_value=[(stored_pin,)])
        )

        assert storage.query_pin(stored_pin) == stored_pin
        assert select_from_mock.call_args.kwargs['query']['value'] == [stored_pin]

    def test_insert_pin(self, mocker):
        connection_mock = mocker.patch('data.storage.database.PostgreSQLConnection')
        storage = database.PostgreSQLStorage(*[_ for _ in range(4)])
        select_from_mock = mocker.patch.object(storage, '_select_from')
        insert_into_mock = mocker.patch.object(storage, '_insert_into')

        pin_data = {
            "url": "url",
            "title": "title",
            "description": "description",
            "dominant_color": "dominant_color",
            "images": ["image_1", "image_2"],
            "hashtags": ["hashtag_1", "hashtag_2"]
        }

        storage.insert_pin(dict(**pin_data))

        assert insert_into_mock.mock_calls[0].kwargs['values'] == [
            pin_data['url'], pin_data['title'],
            pin_data['description'], pin_data['dominant_color']
        ]
        pin_id = select_from_mock.return_value[0][0]

        assert insert_into_mock.mock_calls[1].kwargs['values'] == [
            pin_id, pin_data['images'][0]
        ]
        assert insert_into_mock.mock_calls[2].kwargs['values'] == [
            pin_id, pin_data['images'][1]
        ]

        assert insert_into_mock.mock_calls[3].kwargs['values'] == [
            pin_id, pin_data['hashtags'][0]
        ]
        assert insert_into_mock.mock_calls[4].kwargs['values'] == [
            pin_id, pin_data['hashtags'][1]
        ]


class TestMySQLStorage:
    def test_storage(self, mocker):
        connection_mock = mocker.patch('data.storage.database.MySQLConnection')
        database_config = {"database": "db", "user": "u", "password": "pass",
                           "host": "localhost"}

        database.MySQLStorage(**database_config)

        assert connection_mock.call_args.kwargs == database_config

