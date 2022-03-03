from typing import List, Dict, Union
import psycopg
import mysql.connector


class SQL:
    def insert_into(self, table:str, column:Union[str, list], value):
        """Perform a SQL insert statement.

        INSERT INTO `table` (`column`) VALUES (`value`); .

        Args:
            table: The table to insert into.
            column: The column to insert into.
            value: The value to insert into the column.
        """

        statement = 'INSERT INTO {} ({}) VALUES ({})'.format(
                        table,
                        (('{}, ' * len(column))[:-2]).format(*column),
                        ('%s, ' * len(value))[:-2]
                    )
        self.execute(statement, value)
        self.commit()

    def select_from(self, table:str, column:str, query:Dict[str, str]):
        """Perform a SQL select statement.

        SELECT `column` FROM `table`
        WHERE `query['column']` IN `query['value']`; .

        Args:
            table: The table to perform the query.
            column: The column to perform the query.
            query: The column and its value to query for.

        Returns:
            List[tuple]: The rows matching the query.
        """

        if type(query['value']) is str:
            query['value'] = [query['value']]

        statement = 'SELECT {} FROM {} WHERE {} IN ({})'.format(
            f'{table}.{column}', table, query['column'],
            ('%s, ' * len(query['value']))[:-2]
        )

        self.execute(statement, query['value'])
        return self.fetchall()

    def insert_pin(self, data:Dict[str, Union[str, list]]):
        """Insert the data inside the database.

        Args:
            data: A pin's data.
        """

        # Insert the pin.
        self.insert_into(
            table='pins',
            column=['url', 'title', 'subtitle'],
            value=(data['url'], data['title'], data['subtitle'])
        )

        # Query for the pin id.
        rows = self.select_from(
            column='id', table='pins',
            query={'column': 'url', 'value': data['url']}
        )
        pin_id = [col[0] for col in rows][0]

        # Insert the images.
        for image in data['images']:
            self.insert_into(
                table='images',
                column=['pin_id', 'url'],
                value=(pin_id, image)
            )

    def query_urls(self, urls:List[str]):
        """Query the database for matching URLs.

        Args:
            urls: The URLs to query the database.

        Returns:
            List[str]: The `urls` that are already in the database.
        """

        rows = self.select_from(
            column='url', table='pins',
            query={'column': 'url', 'value': urls}
        )
        return [col[0] for col in rows]


class DBConnection:
    """Manage the connection to the database.

    Args:
        database: The database. E.g. Postgres, MySQL.
        conn_params: The connection parameters.
    """

    def __init__(self, database:str, conn_params:Dict[str, Union[int, str]]):
        self.connection = (database, conn_params)
        self.cursor = self._connection

    @property
    def connection(self):
        """The connection to the database."""

        return self._connection

    @connection.setter
    def connection(self, conn):
        try:
            if conn[0] == 'Postgres':
                self._connection = psycopg.connect(**conn[1])
            elif conn[0] == 'MySQL':
                self._connection = mysql.connector.connect(**conn[1])
        except Exception as e:
            print(e, '\n[!] Error connecting to the database [!]')
            exit()

    @property
    def cursor(self):
        """The connection's cursor."""

        return self._cursor

    @cursor.setter
    def cursor(self, connection):
        self._cursor = connection.cursor()

    def fetchall(self):
        """Return the rows from the database."""

        return self.cursor.fetchall()

    def execute(self, sql:str, params=()):
        """Execute some SQL statement.

        Args:
            sql: The SQL statement.
            params: The values to fill the SQL placeholders.
        """

        self.cursor.execute(sql, params)

    def commit(self):
        """Commit the database records."""

        self.connection.commit()


class Postgres(SQL, DBConnection):
    """Connect to the Postgres database."""

    def __init__(self, conn_params:Dict[str, str]):
        DBConnection.__init__(self, self.__class__.__name__, conn_params)


class MySQL(SQL, DBConnection):
    """Connect to the MySQL database."""

    def __init__(self, conn_params:Dict[str, str]):
        DBConnection.__init__(self, self.__class__.__name__, conn_params)

