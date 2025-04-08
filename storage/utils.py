from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection
import mysql.connector
import psycopg


type BaseMySQLConnection = PooledMySQLConnection | MySQLConnectionAbstract


def connect_to_postgres(
    database: str, user: str, password: str, **extra_opts
) -> psycopg.Connection:

    host = extra_opts.pop("host", "localhost")

    return psycopg.connect(
        dbname=database,
        host=host,
        user=user,
        password=password,
        **extra_opts,
    )


def connect_to_mysql(
    database: str, user: str, password: str, **extra_opts
) -> BaseMySQLConnection:

    return mysql.connector.connect(
        database=database,
        user=user,
        password=password,
        **extra_opts,
    )
