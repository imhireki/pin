import pytest

from storage.utils import connect_to_postgres, connect_to_mysql
import settings


@pytest.mark.postgres
def test_connect_to_postgres():
    with connect_to_postgres(**settings.TEST_DATABASE["POSTGRES"]) as connection:
        assert connection.info.status.value == 0
    assert connection.info.status.value == 1


@pytest.mark.mysql
def test_connect_to_mysql():
    with connect_to_mysql(**settings.TEST_DATABASE["MYSQL"]) as connection:
        assert connection.is_connected()
    assert not connection.is_connected()
