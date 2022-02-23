from .file import JsonFile
from .database import Postgres, MySQL


class Storage:
    @staticmethod
    def postgres(connection):
        return Postgres(connection)

    @staticmethod
    def mysql(connection):
        return MySQL(connection)

    @staticmethod
    def json(filename):
        return JsonFile(filename)
