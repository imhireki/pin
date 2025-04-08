from abc import ABC, abstractmethod

from psycopg.sql import SQL, Composed, Identifier, Placeholder
import psycopg

from storage.utils import BaseMySQLConnection


type SQLConnection = psycopg.Connection | BaseMySQLConnection


class IDatabaseStorage[Connection: SQLConnection](ABC):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    @abstractmethod
    def select_cols_from_table(self, cols: list, table: str, query: dict) -> list:
        pass

    @staticmethod
    def build_select_cols_from_table(cols: list, table: str, query: dict) -> Composed:
        statement = SQL("SELECT ({}) FROM {} WHERE {} IN ({});")

        processed_columns = [
            Identifier(column) if column != "*" else SQL("*") for column in cols
        ]

        composed = statement.format(
            SQL(", ").join(processed_columns),
            Identifier(table),
            Identifier(query["col"]),
            Placeholder(),
        )
        return composed

    @abstractmethod
    def insert_vals_into_cols(self, vals: list, cols: list, table: str) -> int:
        pass

    @staticmethod
    def build_insert_vals_into_cols(vals: list, cols: list, table: str) -> Composed:
        statement = SQL("INSERT INTO {} ({}) VALUES ({});")
        composed = statement.format(
            Identifier(table),
            SQL(", ").join(map(Identifier, cols)),
            SQL(", ").join(Placeholder() for _ in vals),
        )
        return composed

    def is_stored(self, external_id: str) -> bool:
        rows = self.select_cols_from_table(
            ["id"], "pin", {"col": "external_id", "val": external_id}
        )
        return True if rows and rows[0] else False

    def insert_pin(
        self,
        id: str,
        url: str,
        title: str,
        description: str,
        dominant_color: str,
        hashtags: list,
        images: list,
    ) -> None:
        pid = self.insert_vals_into_cols(
            [url, title, description, dominant_color, id],
            ["url", "title", "description", "dominant_color", "external_id"],
            "pin",
        )

        for image in images:
            self.insert_vals_into_cols([pid, image], ["pin_id", "url"], "image")

        for hashtag in hashtags:
            self.insert_vals_into_cols([pid, hashtag], ["pin_id", "hashtag"], "hashtag")


class PostgreSQLStorage(IDatabaseStorage[psycopg.Connection]):
    _connection: psycopg.Connection

    def insert_vals_into_cols(self, vals: list, cols: list, table: str) -> int:
        with self._connection.cursor() as cursor:
            statement = self.build_insert_vals_into_cols(vals, cols, table)
            cursor.execute(statement, vals)
            self._connection.commit()

            cursor.execute("SELECT LASTVAL()")
            most_recent_row = cursor.fetchone()

        if not most_recent_row or not most_recent_row[0]:
            raise Exception("Failed to retrieve last row's id")
        return most_recent_row[0]

    def select_cols_from_table(self, cols: list, table: str, query: dict) -> list:
        with self._connection.cursor() as cursor:
            statement = self.build_select_cols_from_table(cols, table, query)
            cursor.execute(statement, (query["val"],))
            return cursor.fetchall()


class MySQLStorage(IDatabaseStorage[BaseMySQLConnection]):
    _connection: BaseMySQLConnection

    @staticmethod
    def _process_statement(statement: str, dquote=False, parenthesis=True) -> str:
        if not dquote:
            statement = statement.replace('"', "")
        if not parenthesis:
            statement = statement.replace("(", "", 1).replace(")", "", 1)
        return statement

    def insert_vals_into_cols(self, vals: list, cols: list, table: str) -> int:
        with self._connection.cursor() as cursor:
            statement = self.build_insert_vals_into_cols(vals, cols, table).as_string()
            processed = self._process_statement(statement)
            cursor.execute(processed, tuple(vals))

            self._connection.commit()
            row_id = cursor.lastrowid

        if not row_id:
            raise Exception("Failed to retrieve last row's id")
        return row_id

    def select_cols_from_table(self, cols: list, table: str, query: dict) -> list:
        with self._connection.cursor() as cursor:
            statement = self.build_select_cols_from_table(cols, table, query)
            processed = self._process_statement(
                statement.as_string(), parenthesis=False
            )
            cursor.execute(processed, (query["val"],))
            return cursor.fetchall()
