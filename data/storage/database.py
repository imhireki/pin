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

    @property
    def connection(self) -> DBConnection:
        return self._connection

    def get_cursor(self) -> DBCursor:
        return self._connection.cursor()
