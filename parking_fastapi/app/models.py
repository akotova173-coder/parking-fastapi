from datetime import datetime
from typing import List
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship
from .database import Base


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    credit_card = Column(String(50), nullable=True)
    car_number = Column(String(10), nullable=True)

    parkings: Mapped[List["ClientParking"]] = relationship(
        'ClientParking', back_populates='client'
    )

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'credit_card': self.credit_card,
            'car_number': self.car_number,
        }

    def __repr__(self) -> str:
        return f'<Client {self.name} {self.surname}>'


class Parking(Base):
    __tablename__ = 'parking'

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    opened = Column(Boolean, nullable=True, default=True)
    count_places = Column(Integer, nullable=False)
    count_available_places = Column(Integer, nullable=False)

    client_parkings: Mapped[List["ClientParking"]] = relationship(
        'ClientParking', back_populates='parking'
    )

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'address': self.address,
            'opened': self.opened,
            'count_places': self.count_places,
            'count_available_places': self.count_available_places,
        }

    def __repr__(self) -> str:
        return f'<Parking {self.address}>'


class ClientParking(Base):
    __tablename__ = 'client_parking'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    parking_id = Column(Integer, ForeignKey('parking.id'), nullable=False)
    time_in = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_out = Column(DateTime, nullable=True)

    client: Mapped["Client"] = relationship('Client', back_populates='parkings')
    parking: Mapped["Parking"] = relationship('Parking', back_populates='client_parkings')

    __table_args__ = (
        UniqueConstraint('client_id', 'parking_id', name='unique_client_parking'),
    )

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'client_id': self.client_id,
            'parking_id': self.parking_id,
            'time_in': self.time_in.isoformat() if self.time_in else None,
            'time_out': self.time_out.isoformat() if self.time_out else None,
        }

    def __repr__(self) -> str:
        return f'<ClientParking client={self.client_id} parking={self.parking_id}>'
