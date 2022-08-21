from abc import ABC, abstractmethod
from typing import Union, Any

from bs4 import BeautifulSoup
import requests
import json


class IPin(ABC):
    def fetch_data(self) -> dict[str, Union[str, list]]: pass
