from .file import JsonFile
from .database import Postgres, MySQL


def postgres(connection):
    return Postgres(connection)

def mysql(connection):
    return MySQL(connection)

def json(filename):
    return JsonFile(filename)
