import pytest

from storage.database import PostgreSQLStorage, MySQLStorage
from storage.connection import connect_to_postgres, connect_to_mysql
import settings


def test_build_select_cols_from_table():
    select_url_from_pid = PostgreSQLStorage.build_select_cols_from_table(
        ["url"],
        "pin",
        query={"col": "pid", "value": "123"},
    ).as_string()

    select_pid_from_url = PostgreSQLStorage.build_select_cols_from_table(
        ["pid", "title"], "pin", query={"col": "url", "value": "/pin/123/"}
    ).as_string()

    assert select_url_from_pid == 'SELECT ("url") FROM "pin" WHERE "pid" IN (%s);'
    assert (
        select_pid_from_url == 'SELECT ("pid", "title") FROM "pin" WHERE "url" IN (%s);'
    )


def test_build_insert_vals_into_cols():
    insert_into = PostgreSQLStorage.build_insert_vals_into_cols(
        ["/pin/123/", "pin_title"], ["url", "title"], "pin"
    ).as_string()

    assert insert_into == 'INSERT INTO "pin" ("url", "title") VALUES (%s, %s);'


@pytest.mark.parametrize(
    "rows, is_stored",
    [
        [[], False],
        [
            [
                (),
            ],
            False,
        ],
        [["1"], True],
    ],
)
def test_is_stored(mocker, rows, is_stored):
    connection = mocker.Mock()
    storage = PostgreSQLStorage(connection)
    mocker.patch.object(storage, "select_cols_from_table", return_value=rows)

    assert storage.is_stored("123456789") == is_stored


def test_insert(mocker):
    data = {
        "id": "123",
        "url": "/pin/123/",
        "title": "t",
        "description": "d",
        "dominant_color": "#ff0000",
        "hashtags": ["#a"],
        "images": ["img.jpg"],
    }

    storage = PostgreSQLStorage(mocker.Mock())
    insert_vals_into_cols = mocker.patch.object(storage, "insert_vals_into_cols")
    pid = insert_vals_into_cols.return_value

    storage.insert_pin(**data)

    insert_vals_into_cols.assert_any_call(
        ["/pin/123/", "t", "d", "#ff0000", "123"],
        ["url", "title", "description", "dominant_color", "external_id"],
        "pin",
    )

    insert_vals_into_cols.assert_any_call(
        [pid, "#a"],
        ["pin_id", "hashtag"],
        "hashtag",
    )

    insert_vals_into_cols.assert_any_call(
        [pid, "img.jpg"],
        ["pin_id", "url"],
        "image",
    )


@pytest.mark.postgres
class TestPostgreSQLStorage:
    def test_insert_values_into_columns(self):
        with connect_to_postgres(**settings.TEST_DATABASE["POSTGRES"]) as connection:
            storage = PostgreSQLStorage(connection)

            cols = ["url", "title", "description", "dominant_color", "external_id"]
            vals = ["/pin/2/", "title", "description", "#ffffff", "2"]
            pid = storage.insert_vals_into_cols(vals, cols, "pin")

        assert pid and isinstance(pid, int)

    def test_select_column_from_table(self):
        with connect_to_postgres(**settings.TEST_DATABASE["POSTGRES"]) as connection:
            storage = PostgreSQLStorage(connection)

            rows = storage.select_cols_from_table(
                ["dominant_color", "id"], "pin", {"col": "url", "val": "/pin/2/"}
            )
        assert rows and len(rows) > 0


class TestMySQLStorage:
    def test_process_statement(self, mocker):
        storage = MySQLStorage(mocker.Mock())

        processed = storage._process_statement(
            'SELECT ("id", "title") FROM pin WHERE "url" IN (%s);',
            dquote=False,
            parenthesis=False,
        )

        assert processed == "SELECT id, title FROM pin WHERE url IN (%s);"

    @pytest.mark.mysql
    def test_insert_values_into_columns(self):
        with connect_to_mysql(**settings.TEST_DATABASE["MYSQL"]) as connection:
            storage = MySQLStorage(connection)

            cols = ["url", "title", "description", "dominant_color", "external_id"]
            vals = ["/pin/1/", "title", "description", "#ffffff", "1"]
            pid = storage.insert_vals_into_cols(vals, cols, "pin")

        assert pid and isinstance(pid, int)

    @pytest.mark.mysql
    def test_select_column_from_table(self):
        with connect_to_mysql(**settings.TEST_DATABASE["MYSQL"]) as connection:
            storage = MySQLStorage(connection)

            rows = storage.select_cols_from_table(
                ["dominant_color", "id"], "pin", {"col": "url", "val": "/pin/1/"}
            )
        assert rows and len(rows) > 0
