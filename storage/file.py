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
        with open(self._filename, "a") as csv_file:
            writer = csv.writer(csv_file)
            data = [id, url, title, description, dominant_color, hashtags, images]
            writer.writerow(data)

    def is_stored(self, external_id: str) -> bool:
        if not os.path.exists(self._filename):
            return False
        with open(self._filename, "r") as csv_file:
            for data in csv.reader(csv_file):
                if data[0] == external_id:
                    return True
        return False


class JsonStorage(IFileStorage):
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
        data = {
            "id": id,
            "url": url,
            "title": title,
            "description": description,
            "dominant_color": dominant_color,
            "hashtags": hashtags,
            "images": images,
        }
        with open(self._filename, "a") as json_file:
            json_file.write(json.dumps(data) + "\n")

    def is_stored(self, external_id: str) -> bool:
        if not os.path.exists(self._filename):
            return False

        with open(self._filename, "r") as json_file:
            for line in json_file:
                if json.loads(line)["id"] == external_id:
                    return True
        return False
