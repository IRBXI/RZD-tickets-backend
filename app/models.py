from datetime import datetime
from typing import Annotated
from app.services.validation import validate_traincode, validate_date, validate_time, validate_user
from pydantic import BaseModel, AfterValidator, EmailStr, UUID4, ValidationInfo
from pydantic.functional_validators import field_validator


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserRegister(UserBase):
    password: str
    confirmed_password: str

    @field_validator('confirmed_password', mode='after')
    @classmethod
    def check_matching_passwords(cls, value: str, info: ValidationInfo):
        if value != info.data['password']:
            raise ValueError("Passwords do not math")
        return value

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: Annotated[UUID4, AfterValidator(validate_user)]

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
    departure_time: datetime
    arrival_time: datetime
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
