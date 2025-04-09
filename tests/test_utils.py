import pytest

from utils import store_valid_pin


@pytest.mark.parametrize(
    "validity, data, is_stored",
    [
        [True, {"url": "url"}, False],
        [True, {"url": "url"}, True],
        [False, {}, False],
    ],
)
def test_store_valid_pin(mocker, validity, data, is_stored):
    storage = mocker.Mock()
    storage.is_stored.return_value = is_stored

    mocker.patch("utils.PinData")
    pin = mocker.patch("utils.Pin").return_value
    pin.is_valid.return_value = validity
    pin.fetch_data.return_value = data

    store_valid_pin(storage, mocker.Mock(), "123")

    if not validity or is_stored:
        storage.insert_pin.assert_not_called()
    else:
        storage.insert_pin.assert_called_with(**data)
