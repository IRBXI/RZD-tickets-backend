import datetime
from typing import Annotated
from pydantic import BaseModel, AfterValidator
from pydantic import BaseModel, AfterValidator, EmailStr, validator
from app.services.validation import validate_station_code, validate_date, validate_time


StationCode = Annotated[str, AfterValidator(validate_station_code)]


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserRegister(UserBase):
    password: str
    password_again: str

    @validator("confirm_correct")
    def verify_passwords(cls, v, values, **kwargs):
        password = values.get("password")

        if v != password:
            raise ValueError("Passwords do not math")

        return v


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    email: EmailStr
    password: str


class PathSegment(BaseModel):
    start_station_name: str
    end_station_name: str
    start_time: Annotated[str, AfterValidator(validate_time)] = "%H:%M"
    end_time: Annotated[str, AfterValidator(validate_time)] = "%H:%M"


class Car(BaseModel):
    car_number: int
    car_type: str
    free_seats: dict[str, list[PathSegment]]


class CarGroup(BaseModel):
    car_type: str
    free_seats: int
    min_price: int


class Train(BaseModel):
    number: str
    name: str
    origin_station_name: str
    destination_station_name: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    car_groups: list[CarGroup]


class Stop(BaseModel):
    station_name: str
    station_code: StationCode = "2000000"
    date: Annotated[str, AfterValidator(validate_date)] | None
    departure_time: Annotated[str, AfterValidator(validate_time)] | None
    arrival_time: Annotated[str, AfterValidator(validate_time)] | None


class TrainsRequest(BaseModel):
    from_code: StationCode = "2000000"
    to_code: StationCode = "2000000"
    date: Annotated[str, AfterValidator(validate_date)] = "%d.%m.%Y"


class SeatsRequest(BaseModel):
    train_request: TrainsRequest
    train_number: str = "000A"
    departure_time: Annotated[str, AfterValidator(validate_time)] = "%H:%M"
    arrival_time: Annotated[str, AfterValidator(validate_time)] = "%H:%M"
