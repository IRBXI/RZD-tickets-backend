from app.models.db_models import Station
from .abstract_repos import StationRepo
from app.core.exceptions import NoStationException


class TortoiseStationRepo(StationRepo):
    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TortoiseStationRepo, cls).__new__(cls)
        return cls.instance

    @staticmethod
    async def get_station_by_name(name: str) -> Station:
        name = name.upper()
        station = await Station.get_or_none(name=name)

        if station is None:
            raise NoStationException("There is no station in db with this name")

        return station

    @staticmethod
    async def create_station(name: str, station_code: str) -> Station:
        name = name.upper()
        station = await Station.create(id=station_code, name=name)
        return station
