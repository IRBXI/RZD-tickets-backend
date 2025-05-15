from asyncio import sleep
import time
from app.models import (
    Train,
    TrainsRequest,
    SeatsRequest,
    Car,
)
from app.services.url import build_url
from app.services.json_convertion import (
    get_train_list,
    get_stops,
    get_cars,
)
from app.services.train import stops_to_seats_requests, combine_cars_seats_info
from app.util.functional import async_map
from fastapi import APIRouter
from httpx import AsyncClient
from http import HTTPStatus

DEFAULT_URL = "https://pass.rzd.ru"
TIMETABLE_URL = "https://pass.rzd.ru/timetable/public/ru"
GET_TRAINS_URL = build_url(
    TIMETABLE_URL,
    layer_id=5827,
    dir=0,
    tfl=3,
    checkSeats=1,
    md=0,
)
STATIONS_URL = build_url(
    "https://pass.rzd.ru/ticket/services/route/basicRoute",
    STRUCTURE_ID=5418,
)
GET_SEATS_URL = build_url(
    TIMETABLE_URL,
    layer_id=5764,
    dir=0,
    seatDetails=1,
    bEntire="false",
)


router = APIRouter(tags=["train"])
client = AsyncClient()


async def setup_cookies() -> None:
    await client.get(DEFAULT_URL)


async def rzd_post(url: str):
    r = await client.post(url)

    if r.status_code != HTTPStatus.OK or r.json()["result"] == "FAIL":
        return {"error": "Couldn't get the response from RZD"}

    rid = r.json()["RID"]
    url += f"&rid={rid}"

    timeout = time.time() + 60 * 3

    while r.json()["result"] == "RID" and time.time() < timeout:
        r = await client.post(url)
        await sleep(0.5)

    if r.json()["result"] == "RID":
        return {"error": "RZD api unavailable, waited for 3 mins"}

    return r.json()


async def get_train_cars_with_seats(
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

    response_data = await rzd_post(url)

    return get_cars(response_data)


@router.post("/trains/get_trains", response_model=list[Train] | dict)
async def get_train(
    request_data: TrainsRequest,
):
    url = build_url(
        GET_TRAINS_URL,
        code0=request_data.from_code,
        code1=request_data.to_code,
        dt0=request_data.date,
    )

    response_data = await rzd_post(url)

    if "error" in response_data:
        return response_data

    return get_train_list(response_data)


@router.post("/trains/get_seats", response_model=dict[int, Car] | dict)
async def get_train_seats_with_segment_info(
    request_data: SeatsRequest,
):
    url = build_url(
        STATIONS_URL,
        trainNumber=request_data.train_number,
        depDate=request_data.train_request.date,
    )

    response_data = await rzd_post(url)

    if "error" in response_data:
        return response_data

    # json -> list[Stop] -> list[SeatsRequest] -> list[dict[int, Car]] -> dict[int, Car]
    res = get_stops(response_data)
    res = stops_to_seats_requests(request_data.train_number, res)
    res = await async_map(get_train_cars_with_seats, res)
    res = combine_cars_seats_info(res)
    return res
