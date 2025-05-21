from app.models.models import (
    Train,
    TrainsRequest,
    SeatsRequest,
    Car,
)
from app.services.abstract_APIs import TrainAPI
from app.services.rzd_train_API import RZD_TrainAPI
from fastapi import APIRouter, HTTPException
from http import HTTPStatus

router = APIRouter(tags=["train"])

train_api: TrainAPI = RZD_TrainAPI()


@router.post("/trains/get_trains", response_model=list[Train])
async def get_train(
    request_data: TrainsRequest,
):
    try:
        trains = await train_api.get_trains(request_data)
    except TrainAPI.APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    return trains


@router.post("/trains/get_seats", response_model=dict[int, Car])
async def get_seats(
    request_data: SeatsRequest,
):
    try:
        seats_info = await train_api.get_train_seats(request_data)
    except TrainAPI.APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    return seats_info
