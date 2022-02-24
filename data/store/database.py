from typing import List, Dict, Union
import psycopg
import mysql.connector


class SQL:
    def insert_into(self, table:str, column:Union[str, list], value:str):
        statement = 'INSERT INTO {} ({}) VALUES ({})'.format(
                        table,
                        (('{}, ' * len(column))[:-2]).format(*column),
                        ('%s, ' * len(value))[:-2]
                    )
        self.execute(statement, value)
        self.commit()

    def select_from(self, table, column, query:Dict[str, str]):
        """ Perform a SQL select statement

        SELECT `column` FROM `table`
        WHERE `query['column']` IN `query['value']`
        """
        if type(query['value']) is str:
            query['value'] = [query['value']]

        statement = 'SELECT {} FROM {} WHERE {} IN ({})'.format(
            f'{table}.{column}', table, query['column'],
            ('%s, ' * len(query['value']))[:-2]
        )

        self.execute(statement, query['value'])
        return self.fetchall()

    def insert_pin(self, data:Dict[str, list]):
        """Insert the data inside db's tables

        Args:
            data: dictionary with url:str, title:str, subtitle:str, images:list
        """
        self.insert_into(
            table='pins',
            column=['url', 'title', 'subtitle'],
            value=(data['url'], data['title'], data['subtitle'])
        )

        rows = self.select_from(
            column='id', table='pins',
            query={'column': 'url', 'value': data['url']}
        )
        pin_id = [col[0] for col in rows][0]

        # insert the image  FIXME: pins_id to pin_id or pin
        for image in data['images']:
            self.insert_into(
                table='images',
                column=['pins_id', 'url'],
                value=(pin_id, image)
            )

    def query_urls(self, urls:List[str]):
        """Select urls matching `urls` sent in the list.

        Args:
            urls: list of urls used for check the url field in the db.
        Returns:
            list: List[str] if any matches, List[] otherwise.
        """
        rows = self.select_from(
            column='url', table='pins',
            query={'column': 'url', 'value': urls}
        )
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

