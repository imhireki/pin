from requests import Session
from pinterest.pin import Pin, PinData
from storage.database import IDatabaseStorage
from storage.file import IFileStorage


type Storage = IFileStorage | IDatabaseStorage


def store_valid_pin(storage: Storage, session: Session, pin_id: str) -> None:
    pin_data = PinData(pin_id, session)
    pin = Pin(pin_data)

    data = pin.fetch_data()

    if not pin.is_valid() or storage.is_stored(pin_id):
        return

    storage.insert_pin(**data)
