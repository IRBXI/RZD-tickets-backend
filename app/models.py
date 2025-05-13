import datetime
from typing import Annotated
from pydantic import BaseModel, AfterValidator
from app.services.validation import validate_traincode, validate_date, validate_time


class PathSegment(BaseModel):
    start_code: Annotated[str, AfterValidator(validate_traincode)] = "2000000"
    end_code: Annotated[str, AfterValidator(validate_traincode)] = "2000000"
    start_time: Annotated[str, AfterValidator(validate_time)] = "%H:%M"
    end_time: Annotated[str, AfterValidator(validate_time)] = "%H:%M"


class Seat(BaseModel):
    number: str
    free_segments: list[PathSegment]


class Car(BaseModel):
    free_seats: list[Seat]


class CarGroup(BaseModel):
    car_type: str
    free_seats: int
    min_price: int
    cars: list[Car] = []


class Train(BaseModel):
    number: str
    name: str
    origin_station_name: str
    destination_station_name: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    car_groups: list[CarGroup]


class Station(BaseModel):
    name: str
    code: str


class TrainsRequest(BaseModel):
    from_code: Annotated[str, AfterValidator(validate_traincode)] = "2000000"
    to_code: Annotated[str, AfterValidator(validate_traincode)] = "2000000"
    date: Annotated[str, AfterValidator(validate_date)] = "%d.%m.%Y"


class SeatsRequest(BaseModel):
    train_request: TrainsRequest
    train_number: str = "000A"
    departure_time: Annotated[str, AfterValidator(validate_time)] = "%H:%M"
    arrival_time: Annotated[str, AfterValidator(validate_time)] = "%H:%M"
