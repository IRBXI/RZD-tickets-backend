from typing import Iterable
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
from app.services.abstract_services import AbstractTrainService
from app.core.exceptions import APIUnavailableException
from .json_convertion import RzdJsonConverter
from asyncio import sleep
import time
from http import HTTPStatus


DEFAULT_URL: str = "https://pass.rzd.ru"
TIMETABLE_URL: str = "https://pass.rzd.ru/timetable/public/ru"
GET_TRAINS_URL: str = build_url(
    TIMETABLE_URL,
    layer_id=5827,
    dir=0,
    tfl=3,
    checkSeats=1,
    md=0,
)
STATIONS_URL: str = build_url(
    "https://pass.rzd.ru/ticket/services/route/basicRoute",
    STRUCTURE_ID=5418,
)
GET_SEATS_URL: str = build_url(
    TIMETABLE_URL,
    layer_id=5764,
    dir=0,
    seatDetails=1,
    bEntire="false",
)


# Singleton class to represent rzd api
# IMPORTANT!!! : should only be first created by the class create() method
# using default constructor before ever calling create() method will cause an exception
class RzdTrainService(AbstractTrainService):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(RzdTrainService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._client = AsyncClient()

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

    async def _rzd_post(
        self,
        url: str,
    ):
        r = await self._client.post(url)

        timeout = time.time() + 60 * 3
        sleep_time = 0.3

        while (
            r.status_code != HTTPStatus.OK or r.json()["result"] == "FAIL"
        ) and time.time() < timeout:
            await sleep(sleep_time)
            if sleep_time < 1:
                sleep_time *= 2
            else:
                sleep_time **= 2
            r = await self._client.post(url)

        if r.status_code != HTTPStatus.OK or r.json()["result"] == "FAIL":
            raise APIUnavailableException("Couldn't get the response from RZD")

        rid = r.json()["RID"]
        url += f"&rid={rid}"

        timeout = time.time() + 60 * 3
        sleep_time = 0.3

        while r.json()["result"] != "OK" and time.time() < timeout:
            await sleep(sleep_time)
            if sleep_time < 1:
                sleep_time *= 2
            else:
                sleep_time **= 2
            r = await self._client.post(url)

        if r.json()["result"] != "OK":
            raise APIUnavailableException("RZD api unavailable, waited for 1 mins")

        return r.json()

    async def get_trains(
        self,
        request_data: TrainsRequest,
    ) -> list[Train]:
        url = build_url(
            GET_TRAINS_URL,
            code0=request_data.from_code,
            code1=request_data.to_code,
            dt0=request_data.date,
        )

        try:
            response_data = await self._rzd_post(url)
        except APIUnavailableException:
            raise

        return RzdJsonConverter.get_trains_from_json(response_data)

    async def get_train_seats(
        self,
        request_data: SeatsRequest,
    ) -> dict[int, Car]:
        url = build_url(
            STATIONS_URL,
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
        return res

    async def _get_train_cars_with_seats(
        self,
        request_data: SeatsRequest,
    ) -> dict[int, Car]:
        url = build_url(
            GET_SEATS_URL,
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
