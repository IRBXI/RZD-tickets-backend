from app.util.url import build_url
from httpx import AsyncClient
from app.core.exceptions import APIUnavailableException, NoStationException
from app.services.abstract_services import AbstractStationService
from app.repositories import get_station_repo
from app.models.db_models import Station
from asyncio import sleep
import time
from http import HTTPStatus

DEFAULT_URL: str = "https://pass.rzd.ru"
SUGGESTER_URL: str = build_url(
    "https://pass.rzd.ru/suggester",
    compactMode="y",
    lat=1,
    lang="ru",
)


class RzdStationService(AbstractStationService):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(RzdStationService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._client = AsyncClient()
        self.station_repo = get_station_repo()

    @classmethod
    async def create(cls):
        if hasattr(cls, "instance"):
            return cls.instance
        self = cls()
        self.__init__()
        await self._setup_cookies()
        cls.instance = self
        return self

    async def _setup_cookies(self):
        await self._client.get(DEFAULT_URL)

    async def get_station_code(self, name: str) -> str:
        name = name.upper()

        url = build_url(
            SUGGESTER_URL,
            stationNamePart=name,
        )

        response_data = await self._client.get(url)

        timeout = time.time() + 60 * 3
        sleep_time = 0.3

        while response_data.status_code != HTTPStatus.OK and time.time() < timeout:
            await sleep(sleep_time)
            if sleep_time < 1:
                sleep_time *= 2
            else:
                sleep_time **= 2
            response_data = await self._client.get(url)

        if response_data.status_code != HTTPStatus.OK:
            raise APIUnavailableException("Couldn't get the response from RZD")

        # first search for an exact match
        for station in response_data.json():
            if station["n"] == name:
                return str(station["c"])

        # then search for a name which has a name we are searching for as a substring
        for station in response_data.json():
            if name in station["n"]:
                return str(station["c"])

        raise NoStationException("There is no station with such name")

    async def get_station_by_name(self, name: str) -> Station:
        try:
            station = await self.station_repo.get_station_by_name(name)
            return station
        except NoStationException:
            try:
                station_code = await self.get_station_code(name)
                return await self.create_station(name, station_code)
            except APIUnavailableException:
                raise
            except NoStationException:
                raise

    async def create_station(self, name: str, station_code: str) -> Station:
        return await self.station_repo.create_station(name, station_code)
