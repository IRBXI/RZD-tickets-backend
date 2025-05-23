from typing import Awaitable, Iterable
from app.models import (
    Stop,
    SeatsRequest,
    StationCode,
    TrainsRequest,
    Car,
    Train,
    StationCode,
)
from asyncio import gather
from app.util.url import build_url
from app.util.async_helpers import offset_coroutine
from httpx import AsyncClient
from .abstract_APIs import TrainAPI, StationAPI, APIUnavailableException
from .rzd_json_convertion import RzdJsonConverter
from asyncio import sleep
import time
from http import HTTPStatus


# Singleton classes to represent rzd api
# IMPORTANT!!! : should only be first created by the class create() method
# using default constructor before ever calling create() method will cause an exception


class RZD_TrainAPI(TrainAPI):
    _DEFAULT_URL = "https://pass.rzd.ru"
    _TIMETABLE_URL = "https://pass.rzd.ru/timetable/public/ru"
    _GET_TRAINS_URL = build_url(
        _TIMETABLE_URL,
        layer_id=5827,
        dir=0,
        tfl=3,
        checkSeats=1,
        md=0,
    )
    _STATIONS_URL = build_url(
        "https://pass.rzd.ru/ticket/services/route/basicRoute",
        STRUCTURE_ID=5418,
    )
    _GET_SEATS_URL = build_url(
        _TIMETABLE_URL,
        layer_id=5764,
        dir=0,
        seatDetails=1,
        bEntire="false",
    )

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(RZD_TrainAPI, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._client = AsyncClient()

    @classmethod
    async def create(cls):
        self = cls()
        self.__init__()
        await self._setup_cookies()
        cls.instance = self
        return self

    async def _setup_cookies(self):
        await self._client.get(RZD_TrainAPI._DEFAULT_URL)

    async def _rzd_post(
        self,
        url: str,
    ):
        r = await self._client.post(url)

        if r.status_code != HTTPStatus.OK or r.json()["result"] == "FAIL":
            raise APIUnavailableException("Couldn't get the response from RZD")

        if r.json()["result"] == "OK":
            return r.json()

        rid = r.json()["RID"]
        url += f"&rid={rid}"

        timeout = time.time() + 60

        while r.json()["result"] != "OK" and time.time() < timeout:
            r = await self._client.post(url)
            await sleep(1)

        if r.json()["result"] != "OK":
            raise APIUnavailableException("RZD api unavailable, waited for 1 mins")

        return r.json()

    async def get_trains(
        self,
        request_data: TrainsRequest,
    ) -> Awaitable[list[Train]]:
        url = build_url(
            RZD_TrainAPI._GET_TRAINS_URL,
            code0=request_data.from_code,
            code1=request_data.to_code,
            dt0=request_data.date,
        )

        try:
            response_data = await self._rzd_post(url)
        except APIUnavailableException:
            raise

        return RzdJsonConverter.get_trains_from_json(response_data)  # type: ignore

    async def get_train_seats(
        self,
        request_data: SeatsRequest,
    ) -> Awaitable[dict[int, Car]]:
        url = build_url(
            RZD_TrainAPI._STATIONS_URL,
            trainNumber=request_data.train_number,
            depDate=request_data.train_request.date,
        )

        try:
            response_data = await self._rzd_post(url)
        except APIUnavailableException:
            raise

        # json -> list[Stop] -> list[SeatsRequest] -> list[dict[int, Car]] -> dict[int, Car]
        res = RzdJsonConverter.get_stops_from_json(response_data)
        res = self._stops_to_seats_requests(request_data.train_number, res)
        coroutines = [
            offset_coroutine(self._get_train_cars_with_seats(x), i * 0.3)
            for i, x in enumerate(res)
        ]
        res = await gather(*coroutines)
        res = self._combine_cars_seats_info(res)
        return res  # type: ignore

    async def _get_train_cars_with_seats(
        self,
        request_data: SeatsRequest,
    ) -> dict[int, Car]:
        url = build_url(
            RZD_TrainAPI._GET_SEATS_URL,
            tnum0=request_data.train_number,
            dt0=request_data.train_request.date,
            time0=request_data.departure_time,
            time1=request_data.arrival_time,
            code0=request_data.train_request.from_code,
            code1=request_data.train_request.to_code,
        )

        response_data = await self._rzd_post(url)

        return RzdJsonConverter.get_cars_from_json(response_data)

    @staticmethod
    def _stops_to_seats_requests(
        train_number: StationCode,
        stops: list[Stop],
    ) -> list[SeatsRequest]:
        return [
            # There is "type: ignore" here because we know that date, departure_time and arrival_time can't
            # be None in this context
            SeatsRequest(
                train_number=train_number,
                train_request=TrainsRequest(
                    from_code=stops[i - 1].station_code,
                    to_code=stops[i].station_code,
                    date=stops[i - 1].date,  # type: ignore
                ),
                departure_time=stops[i - 1].departure_time,  # type: ignore
                arrival_time=stops[i].arrival_time,  # type: ignore
            )
            for i in range(1, len(stops))
        ]

    @staticmethod
    def _combine_cars_seats_info(
        cars_for_segment: Iterable[dict[int, Car]],
    ) -> dict[int, Car]:
        res: dict[int, Car] = {}
        for cars in cars_for_segment:
            for car_number, car in cars.items():
                for seat, path_segments in car.free_seats.items():
                    if car_number not in res:
                        res[car_number] = car
                        break
                    if seat not in res[car_number].free_seats:
                        res[car_number].free_seats[seat] = []
                    res[car_number].free_seats[seat].append(path_segments[0])
        return res


class RZD_StationAPI(StationAPI):
    _SUGGESTER_URL = build_url(
        "https://pass.rzd.ru/suggester",
        compactMode="y",
        lat=1,
        lang="ru",
    )

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(RZD_StationAPI, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._client = AsyncClient()

    @classmethod
    async def create(cls):
        self = cls()
        self.__init__()
        await self._setup_cookies()
        cls.instance = self
        return self

    async def _setup_cookies(self):
        await self._client.get(RZD_TrainAPI._DEFAULT_URL)

    async def get_station_code(self, name: str) -> Awaitable[str]:
        name = name.upper()

        url = build_url(
            RZD_StationAPI._SUGGESTER_URL,
            stationNamePart=name,
        )

        response_data = await self._client.get(url)

        timeout = time.time() + 60

        while response_data.status_code != HTTPStatus.OK and time.time() < timeout:
            response_data = await self._client.get(url)
            await sleep(1)

        if response_data.status_code != HTTPStatus.OK:
            raise APIUnavailableException("Couldn't get the response from RZD")

        # first search for an exact match
        for station in response_data.json():
            if station["n"] == name:
                return str(station["c"])  # type: ignore

        # then search for a name which has a name we are searching for as a substring
        for station in response_data.json():
            if name in station["n"]:
                return str(station["c"])  # type: ignore

        return ""  # type: ignore
