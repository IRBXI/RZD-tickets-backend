from typing import Self
from app.models import Stop, SeatsRequest, StationCode, TrainsRequest, Car, Train
from app.util.url import build_url
from app.util.functional import async_map
from httpx import AsyncClient
from .train_api import TrainAPI
from .rzd_json_convertion import RzdJsonConverter
from asyncio import sleep
import time
from http import HTTPStatus


# A singleton class to represent rzd train api
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
    async def create(cls) -> Self:
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
            raise TrainAPI.APIUnavailableException("Couldn't get the response from RZD")

        rid = r.json()["RID"]
        url += f"&rid={rid}"

        timeout = time.time() + 60 * 3

        while r.json()["result"] == "RID" and time.time() < timeout:
            r = await self._client.post(url)
            await sleep(0.5)

        if r.json()["result"] == "RID":
            raise TrainAPI.APIUnavailableException(
                "RZD api unavailable, waited for 3 mins"
            )

        return r.json()

    async def get_trains(
        self,
        request_data: TrainsRequest,
    ) -> list[Train]:
        url = build_url(
            RZD_TrainAPI._GET_TRAINS_URL,
            code0=request_data.from_code,
            code1=request_data.to_code,
            dt0=request_data.date,
        )

        try:
            response_data = await self._rzd_post(url)
        except TrainAPI.APIUnavailableException:
            raise

        return RzdJsonConverter.get_trains_from_json(response_data)

    async def get_train_seats(
        self,
        request_data: SeatsRequest,
    ) -> dict[int, Car]:
        url = build_url(
            RZD_TrainAPI._STATIONS_URL,
            trainNumber=request_data.train_number,
            depDate=request_data.train_request.date,
        )

        try:
            response_data = await self._rzd_post(url)
        except TrainAPI.APIUnavailableException:
            raise

        # json -> list[Stop] -> list[SeatsRequest] -> list[dict[int, Car]] -> dict[int, Car]
        res = RzdJsonConverter.get_stops_from_json(response_data)
        res = self._stops_to_seats_requests(request_data.train_number, res)
        res = await async_map(self._get_train_cars_with_seats, res)
        res = self._combine_cars_seats_info(res)
        return res

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
        cars_for_segment: list[dict[int, Car]],
    ) -> dict[int, Car]:
        res: dict[int, Car] = {}
        for cars in cars_for_segment:
            for car_number, car in cars.items():
                for seat, path_segments in car.free_seats.items():
                    if car_number not in res:
                        res[car_number] = car
                        break
                    res[car_number].free_seats.get(seat, []).append(path_segments[0])
        return res
