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

