from typing import List, Dict, Union
import psycopg
import mysql.connector


class SQL:
    def __init__(self, connection:Dict[str, str]):
        pass

    def insert(self, data:Dict[str, list]):
        """Insert the data inside db's tables

        Args:
            data: dictionary with url:str, title:str, subtitle:str, images:list
        """

        # inserting url title e subtitle
        self.cursor.execute(
            """
            INSERT INTO
                pins (url, title, subtitle)
            VALUES
                (%s, %s, %s)
            ;
            """,
            (data['url'], data['title'], data['subtitle'])
        )
        self.connection.commit()  # maybe just one commit

        # query the id from the last insertion
        self.cursor.execute(
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
        rows = self.cursor.fetchall()
        pin_id = [col[0] for col in rows][0]

        for image in data['images']:
            # insert the image  FIXME: pins_id to pin_id or pin
            self.cursor.execute(
                """
                INSERT INTO
                    images (pins_id, url)
                VALUES
                    (%s, %s)
                ;
                """,
                (pin_id, image)
            )
            self.connection.commit()  # maybe just one commit

    def select(self, urls:List[str]):
        """Select urls matching `urls` sent in the list.

        Args:
            urls: list of urls used for check the url field in the db.
        Returns:
            list: List[str] if any matches, List[] otherwise.
        """
        self.cursor.execute(
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
        rows = self.cursor.fetchall()
        return [col[0] for col in rows]


class Postgres(SQL):
    def __init__(self, connection:Dict[str, str]):
        self.connection = psycopg.connect(**connection)
        return super().__init__(self)
        self.cursor = self.connection.cursor()


class MySQL(SQL):
    def __init__(self, connection:Dict[str, str]):
        self.connection = mysql.connector.connect(**connection)
        self.cursor = self.connection.cursor()
