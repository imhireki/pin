from typing import List, Dict, Union
import psycopg
import mysql.connector


class SQL:
    def insert(self, data:Dict[str, list]):
        """Insert the data inside db's tables

        Args:
            data: dictionary with url:str, title:str, subtitle:str, images:list
        """
        # inserting url title e subtitle
        self.execute(
            """
            INSERT INTO
                pins (url, title, subtitle)
            VALUES
                (%s, %s, %s)
            ;
            """,
            (data['url'], data['title'], data['subtitle'])
        )

        self.commit()

        # query the id from the last insertion
        self.execute(
            """
            SELECT
                pin.id
            FROM
                pins as pin
            WHERE
                pin.url = %s
            ;
            """,
            [data['url']]
        )
        rows = self.fetchall()
        pin_id = [col[0] for col in rows][0]

        for image in data['images']:
            # insert the image  FIXME: pins_id to pin_id or pin
            self.execute(
                """
                INSERT INTO
                    images (pins_id, url)
                VALUES
                    (%s, %s)
                ;
                """,
                (pin_id, image)
            )

            self.commit()

    def select(self, urls:List[str]):
        """Select urls matching `urls` sent in the list.

        Args:
            urls: list of urls used for check the url field in the db.
        Returns:
            list: List[str] if any matches, List[] otherwise.
        """
        self.execute(
            """
            SELECT
                pin.url
            FROM
                pins as pin
            WHERE
                pin.url in ({})
            ;
            """.format(('%s, ' * len(urls))[:-2]),  # %s for each url
            urls
        )
        rows = self.fetchall()
        return [col[0] for col in rows]


class DBConnection:
    def __init__(self, database:str, conn_params:Dict[str, Union[int, str]]):
        self.connection = (database, conn_params)
        self.cursor = self._connection

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, conn):
        try:
            # Connection
            if conn[0] == 'Postgres':
                self._connection = psycopg.connect(**conn[1])
            elif conn[0] == 'MySQL':
                self._connection = mysql.connector.connect(conn[1])
        except Exception as e:
            print(e, '\n[!] Error connecting to the database [!]')
            exit()

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, connection):
        if isinstance(connection, psycopg.Connection):
            self._cursor = connection.cursor()

    def fetchall(self):
        return self._cursor.fetchall()

    def execute(self, sql:str, params=()):
        return self.cursor.execute(sql, params)

    def commit(self):
        return self._connection.commit()


class Postgres(DBConnection, SQL):
    def __init__(self, conn_params:Dict[str, str]):
        DBConnection.__init__(self, self.__class__.__name__, conn_params)


class MySQL(SQL, DBConnection):
    def __init__(self, conn_params:Dict[str, str]):
        DBConnection.__init__(self, self.__class__.__name__, conn_params)

