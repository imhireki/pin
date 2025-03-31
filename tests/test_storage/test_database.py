from storage import database


def test_postgresql_connection(mocker):
    connect_mock = mocker.patch("psycopg.connect")
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
    connect_mock = mocker.patch("mysql.connector.connect")
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


def test_postgre_sql_storage(mocker):
    base_connection_options = {"user": "user", "password": 123}
    connection_mock = mocker.patch("storage.database.PostgreSQLConnection")

    postgresql_storage = database.PostgreSQLStorage(
        database="db", **base_connection_options
    )

    assert connection_mock.call_args.kwargs == {
        "dbname": "db",
        "host": "localhost",
        **base_connection_options,
    }
    assert postgresql_storage.connection is connection_mock.return_value


def test_mysql_storage(mocker):
    connection_options = {
        "database": "db",
        "host": "localhost",
        "user": "u",
        "password": "pass",
    }
    connection_mock = mocker.patch("storage.database.MySQLConnection")

    mysql_storage = database.MySQLStorage(**connection_options)

    assert connection_mock.call_args.kwargs == connection_options
    assert mysql_storage.connection is connection_mock.return_value


def test_sql_storage_query_pin(mocker):
    connection_mock = mocker.patch("storage.database.PostgreSQLConnection")
    stored_pin = "https://www.pinterest.com/pin/123/"

    storage = database.PostgreSQLStorage("db", "user", "pass")
    mocker.patch.object(
        storage, "_select_from", mocker.Mock(return_value=[(stored_pin,)])
    )
    query_pin_result = storage.query_pin(stored_pin)

    assert query_pin_result == stored_pin


def test_sql_storage_insert_pin(mocker, pin_data):
    connection_mock = mocker.patch("storage.database.PostgreSQLConnection")
    storage = database.PostgreSQLStorage("db", "user", "pass")
    select_from_mock = mocker.patch.object(storage, "_select_from")
    insert_into_mock = mocker.patch.object(storage, "_insert_into")

    storage.insert_pin(dict(**pin_data))
    pin_id = select_from_mock.return_value[0][0]

    assert insert_into_mock.mock_calls[0].kwargs["values"] == [
        pin_data["url"],
        pin_data["title"],
        pin_data["description"],
        pin_data["dominant_color"],
    ]
    assert insert_into_mock.mock_calls[1].kwargs["values"] == [
        pin_id,
        pin_data["images"][0],
    ]
    assert insert_into_mock.mock_calls[2].kwargs["values"] == [
        pin_id,
        pin_data["hashtags"][0],
    ]
