from app.models.models import (
    Train,
    TrainsRequest,
    SeatsRequest,
    Car,
)
from app.services.train_api import TrainAPI
from app.services.rzd_api import RZD_TrainAPI
from fastapi import APIRouter, HTTPException
from http import HTTPStatus

router = APIRouter(tags=["train"])

train_api: RZD_TrainAPI


async def setup_api():
    global train_api
    train_api = await RZD_TrainAPI.create()


@router.post("/trains/get_trains", response_model=list[Train] | dict)
async def get_train(
    request_data: TrainsRequest,
):
    try:
        trains = await train_api.get_trains(request_data)
    except TrainAPI.APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    return trains


@router.post("/trains/get_seats", response_model=dict[int, Car] | dict)
async def get_seats(
    request_data: SeatsRequest,
):
    try:
        seats_info = await train_api.get_train_seats(request_data)
    except TrainAPI.APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    return seats_info
