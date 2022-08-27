from data.storage import database


def test_postgresql_connection(mocker):
    connect_mock = mocker.patch('psycopg.connect')
    connection_options = {"dbname": "dbname", "password": 123}
    connection = database.PostgreSQLConnection(**connection_options)

    connection.connect()
    connection.disconnect()
    cursor = connection.get_cursor()

    assert connect_mock.call_args.kwargs == connection_options
    assert connection.connection.close.called
    assert cursor == connection.connection.cursor.return_value
