from abc import ABC, abstractmethod
import os.path
import json
import csv


class IFileStorage(ABC):
    def __init__(self, filename: str) -> None:
        self._filename = filename

    @abstractmethod
    def insert_pin(
        self,
        id: str,
        url: str,
        title: str,
        description: str,
        dominant_color: str,
        hashtags: list,
        images: list,
    ) -> None:
        pass

    @abstractmethod
    def is_stored(self, external_id: str) -> bool:
        pass


class CSVStorage(IFileStorage):
    def __init__(self, filename: str) -> None:
        self._filename: str = filename

    def insert_pin(self, data: dict) -> None:
        with open(self._filename, "a") as csv_file:
            pin_writer = csv.writer(csv_file)
            pin_writer.writerow(list(data.values()))

    def query_pin(self, url: str) -> str:
        if not os.path.exists(self._filename):
            return ""

        with open(self._filename, "r") as csv_file:
            for data in csv.reader(csv_file):
                if data[0] == url:
                    return url
            return ""


class JsonStorage(IFileStorage):
    def __init__(self, filename: str) -> None:
        self._filename: str = filename

    def _get_json_data(self) -> list[dict]:
        if not os.path.exists(self._filename):
            return []

        with open(self._filename, "r") as json_file:
            json_data = json.load(json_file) or []
        return json_data

    def insert_pin(self, data: dict) -> None:
        json_data = self._get_json_data()
        json_data.append(data)

        with open(self._filename, "w") as json_file:
            json.dump(json_data, json_file)

    def query_pin(self, url: str) -> str:
        for data in self._get_json_data():
            if data["url"] == url:
                return url
        return ""
