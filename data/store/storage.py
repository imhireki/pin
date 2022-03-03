from .database import Postgres, MySQL
from .file import JsonFile


def postgres(connection):
    """Return a Postgres database storage instance."""
    return Postgres(connection)

def mysql(connection):
    """Return a MySQL database storage instance."""
    return MySQL(connection)

def json(filename):
    """Return a Json file storage instance."""
    return JsonFile(filename)
