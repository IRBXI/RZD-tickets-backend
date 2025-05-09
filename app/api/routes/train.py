from asyncio import sleep
from app.models import Train
from app.util.json_converter import get_train_list
from fastapi import APIRouter
from httpx import AsyncClient
from http import HTTPStatus

DEFAULT_URL = "https://pass.rzd.ru"
GET_TRAINS_URL = "https://pass.rzd.ru/timetable/public/ru?layer_id=5827&dir=0&tfl=3&checkSeats=1&md=0"


router = APIRouter(tags=["train"])
client = AsyncClient()


async def setup_cookies() -> None:
    await client.get(DEFAULT_URL)


# TODO: Rewrite it using the new version of rzd api
@router.get("/trains/get_trains", response_model=list[Train])
async def get_train(
    from_code: str = "2000000", to_code: str = "2000000", date: str = "%d.%m.%Y"
):
    url = f"{GET_TRAINS_URL}&code0={from_code}&code1={to_code}&dt0={date}"
    r = await client.post(url)
    if r.status_code != HTTPStatus.OK or r.json()["result"] == "FAIL":
        return {"error": "Couldn't get the response from rzd"}
    rid = r.json()["RID"]
    url += f"&rid={rid}"
    # for whatever reason it is needed
    # maybe can set a lesser time but this one is more safe
    await sleep(1)
    r = await client.post(url)
    return get_train_list(r.json())
