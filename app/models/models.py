from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, AfterValidator, EmailStr, UUID4, ValidationInfo
from pydantic.functional_validators import field_validator
from .validation import (
    validate_station_code,
    validate_date,
    validate_time,
    validate_user,
)


StationCode = Annotated[str, AfterValidator(validate_station_code)]


class SuccessfulResponse(BaseModel):
    msg: str


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserRegister(UserBase):
    password: str
    confirmed_password: str

    @field_validator("confirmed_password", mode="after")
    @classmethod
    def check_matching_passwords(cls, value: str, info: ValidationInfo):
        if value != info.data["password"]:
            raise ValueError("Passwords do not math")
        return value


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: Annotated[UUID4, AfterValidator(validate_user)]

    class Config:
        orm_mode = True

    @field_validator("id", mode="after")
    def convert_to_str(cls, value: str):
        return str(value) if value else value


class UserLogin(UserBase):
    email: EmailStr
    password: str


class JwtTokenSchema(BaseModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(BaseModel):
    access: JwtTokenSchema
    refresh: JwtTokenSchema


class RefreshToken(BaseModel):
    refresh: str


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
    departure_time: datetime
    arrival_time: datetime
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
