from datetime import datetime
from typing import List
from sqlalchemy.orm import Mapped
from .extensions import db


class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50), nullable=True)
    car_number = db.Column(db.String(10), nullable=True)

    parkings: Mapped[List["ClientParking"]] = db.relationship(
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


class Parking(db.Model):
    __tablename__ = 'parking'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, nullable=True, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    client_parkings: Mapped[List["ClientParking"]] = db.relationship(
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


class ClientParking(db.Model):
    __tablename__ = 'client_parking'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    parking_id = db.Column(db.Integer, db.ForeignKey('parking.id'), nullable=False)
    time_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_out = db.Column(db.DateTime, nullable=True)

    client: Mapped["Client"] = db.relationship('Client', back_populates='parkings')
    parking: Mapped["Parking"] = db.relationship('Parking', back_populates='client_parkings')

    __table_args__ = (
        db.UniqueConstraint('client_id', 'parking_id', name='unique_client_parking'),
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
