from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    name: str
    surname: str
    credit_card: Optional[str] = None
    car_number: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ParkingBase(BaseModel):
    address: str
    opened: Optional[bool] = True
    count_places: int


class ParkingCreate(ParkingBase):
    pass


class Parking(ParkingBase):
    id: int
    count_available_places: int

    model_config = ConfigDict(from_attributes=True)


class ClientParkingBase(BaseModel):
    client_id: int
    parking_id: int


class ClientParkingCreate(ClientParkingBase):
    pass


class ClientParking(ClientParkingBase):
    id: int
    time_in: datetime
    time_out: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ExitResponse(BaseModel):
    message: str
    amount_charged: int
    record: ClientParking
