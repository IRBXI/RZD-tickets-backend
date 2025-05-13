from asyncio import sleep
from app.models import Train, Station, TrainsRequest, SeatsRequest
from app.util.helpers import build_url
from app.util.json_converter import get_train_list
from fastapi import APIRouter
from httpx import AsyncClient
from http import HTTPStatus

DEFAULT_URL = "https://pass.rzd.ru"
GET_TRAINS_URL = build_url(
    "https://pass.rzd.ru/timetable/public/ru",
    {"layer_id": "5827", "dir": "0", "tfl": "3", "checkSeats": "1", "md": "0"},
)
STATIONS_URL = build_url(
    "https://pass.rzd.ru/ticket/services/route/basicRoute", {"STRUCTURE_ID": "5418"}
)


router = APIRouter(tags=["train"])
client = AsyncClient()


async def setup_cookies() -> None:
    await client.get(DEFAULT_URL)


async def rzd_post(url: str) -> dict:
    r = await client.post(url)
    if r.status_code != HTTPStatus.OK or r.json()["result"] == "FAIL":
        return {"error": "Couldn't get the response from rzd"}

    rid = r.json()["RID"]
    url += f"&rid={rid}"

    # for whatever reason it is needed
    # maybe can set a lesser time but this one is more safe
    await sleep(1)

    r = await client.post(url)

    return r.json()


@router.post("/trains/get_trains", response_model=list[Train])
async def get_train(
    request_data: TrainsRequest,
):
    url = build_url(
        GET_TRAINS_URL,
        {
            "code0": request_data.from_code,
            "code1": request_data.to_code,
            "dt0": request_data.date,
        },
    )

    response_data = await rzd_post(url)

    if "error" in response_data:
        return response_data

    return get_train_list(response_data)


@router.post("/trains/get_seats")
async def get_train_seats(
    request_data: SeatsRequest,
):
    url = build_url(
        STATIONS_URL,
        {
            "trainNumber": request_data.train_number,
            "depDate": request_data.train_request.date,
        },
    )

    response_data = await rzd_post(url)

    if "error" in response_data:
        return response_data

    # not done yet
    pass
