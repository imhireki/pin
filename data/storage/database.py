from abc import ABC, abstractmethod
from typing import Union, Any

import mysql.connector
import psycopg


DBConnection = Union[psycopg.Connection, mysql.connector.MySQLConnection]
DBCursor = Union[psycopg.Cursor, mysql.connector.cursor.MySQLCursor]


class ISQLConnection:
    def __init__(self, **connection_options) -> None:
        self._connection_options: dict[str, Any] = connection_options
        self._connection: DBConnection = None

    @abstractmethod
    def connect(self) -> None: pass

    def disconnect(self) -> None:
        self._connection.close()

    def commit(self) -> None:
        self._connection.commit()

    @property
    def connection(self) -> DBConnection:
        return self._connection

    def get_cursor(self) -> DBCursor:
        return self._connection.cursor()


class PostgreSQLConnection(ISQLConnection):
    _connection: psycopg.Connection

    def connect(self) -> None:
        self._connection = psycopg.connect(**self._connection_options)


class MySQLConnection(ISQLConnection):
    _connection: mysql.connector.MySQLConnection

    def connect(self) -> None:
        self._connection = mysql.connector.connect(**self._connection_options)


class IDatabaseStorage(ABC):
    @property
    def connection(self):
        return self._connection

    def _insert_into(self, table: str, columns: list[str], values: list[str]) -> None:
        cursor = self._connection.get_cursor()

        column_slots = (('{}, ' * len(columns))[:-2]).format(*columns)
        column_value_slots = ('%s, ' * len(values))[:-2]

        sql_statement = 'INSERT INTO {} ({}) VALUES ({});'.format(
            table, column_slots, column_value_slots
        )

        cursor.execute(sql_statement, values)
        cursor.close()
        self._connection.commit()

    def _select_from(self, table: str, column: list[str], query: list[str]) -> dict:
        cursor = self._connection.get_cursor()

        table_column = f'{table}.{column}'
        column_value_slots = ('%s, ' * len(query['value']))[:-2]

        sql_statement = 'SELECT {} FROM {} WHERE {} IN ({});'.format(
            table_column, table, query['column'], column_value_slots
        )

        cursor.execute(sql_statement, query['value'])
        fetched_rows = cursor.fetchall()
        cursor.close()
        return fetched_rows

    def insert_pin(self, pin_data: dict[str, Union[str, list]]) -> None:
        hashtags = pin_data.pop('hashtags')
        images = pin_data.pop('images')

        self._insert_into(
            table='pin',
            columns=['url', 'title', 'description', 'dominant_color'],
            values=list(pin_data.values())
        )

        selected_rows_with_id = self._select_from(
            column='id', table='pin',
            query={"column": "url", "value": [pin_data['url']]}
        )
        pin_id = selected_rows_with_id[0][0]

        for image in images:
            self._insert_into(
                table='image',
                columns=['pin_id', 'url'],
                values=[pin_id, image]
            )

        for hashtag in hashtags:
            self._insert_into(
                table='hashtag',
                columns=['pin_id', 'hashtag'],
                values=[pin_id, hashtag]
            )

    def query_pin(self, url: str) -> str:
        selected_rows_with_url = self._select_from(
            column='url', table='pin',
            query={"column": "url", "value": [url]}
        )
        if not selected_rows_with_url:
            return
        return selected_rows_with_url[0][0]


class PostgreSQLStorage(IDatabaseStorage):
    def __init__(self, database: str, user: str, password: str, host: str, **extra_options) -> None:
        self._connection = PostgreSQLConnection(
            dbname=database, user=user, password=password, host=host, **extra_options
        )
        self._connection.connect()

