from typing import List, Dict, Union
import os.path
import json


class JsonFile:
    """Manage the storage as a json file.

    Args:
        filename: the name of the json file.

    Attributes:
        filename: the name of the json file.
    """

    def __init__(self, filename:str):
        self.filename = filename

    @staticmethod
    def url_as_key(data) -> Dict[str, Union[str, list]]:
        """Set the url as the dict key.

        Returns:
            Dict[str, Union[str, list]]: The data with the url as key.
        """

        return {data.pop('url'): dict(**data)}

    def insert_pin(self, data:Dict[str, Union[str, list]]):
        """Append the data to `self.filename`.

        Args:
            data: A pin's data.
        """

        json_data = self.select()
        json_data.update(self.url_as_key(data))

        json_file = open(self.filename, 'w')
        json.dump(obj=json_data, fp=json_file, indent=4)
        json_file.close()

    def query_urls(self, urls:List[str]) -> List[str]:
        """Query the json for matching URLs.

        Args:
            urls: The URLs to query the json file.

        Returns:
            List[str]: The `urls` that are already in the json file.
        """

        json_urls = self.select().keys()
        return [url for url in urls if url in json_urls]

    def select(self) -> Dict[str, Union[str, list]]:
        """Return all the data from `self.filename` json file."""

        if not os.path.exists(self.filename):
            return {}  # the file is created just on insert()

        json_file = open(self.filename, 'r')
        json_data = json.load(json_file)
        json_file.close()
        return json_data

