from app.models.db_models import Station
from typing import Awaitable
from abc import ABC, abstractmethod


class StationsRepo(ABC):
    @staticmethod
    @abstractmethod
    async def get_station_by_name(name: str) -> Awaitable[Station]:
        pass

    @staticmethod
    @abstractmethod
    async def create_station(name: str, station_code: str) -> Awaitable[Station]:
        pass

    class NoStationException(Exception):
        pass
