from abc import ABC, abstractmethod
from typing import Union
import json
import csv
import os


class IFileStorage(ABC):
    @abstractmethod
    def insert_pin(self) -> None: pass

    @abstractmethod
    def query_pin(self, url: str) -> str: pass


class CSVStorage(IFileStorage):
    def __init__(self, filename: str) -> None:
        self._filename: str = filename

    def insert_pin(self, data: dict[str, Union[str, list]]) -> None:
        with open(self._filename, 'a') as csv_file:
            pin_writer = csv.writer(csv_file)
            pin_writer.writerow(data)

    def query_pin(self, url: str) -> str:
        if not os.path.exists(self._filename):
            return None

        with open(self._filename, 'r') as csv_file:
            csv_data = list(csv.reader(csv_file)) or []

        for data in csv_data:
            if data['url'] == url:
                return url
        return None


class JsonStorage(IFileStorage):
    def __init__(self, filename: str) -> None:
        self._filename: str = filename

    def _get_json_data(self) -> list[dict]:
        if not os.path.exists(self._filename):
            return []

        with open(self._filename, 'r') as json_file:
            json_data = json.load(json_file) or []
        return json_data

    def insert_pin(self, data: dict[str, Union[str, list]]) -> None:
        json_data = self._get_json_data()
        json_data.append(data)

        with open(self._filename, 'w') as json_file:
            json.dump(json_data, json_file)

    def query_pin(self, url: str) -> str:
        for data in self._get_json_data():
            if data['url'] == url:
                return url
        return None
