from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    credit_card = Column(String(50), nullable=True)
    car_number = Column(String(10), nullable=True)

    parkings = relationship("ClientParking", back_populates="client")

class Parking(Base):
    __tablename__ = "parkings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(100), nullable=False)
    opened = Column(Boolean, default=True)
    count_places = Column(Integer, nullable=False)
    count_available_places = Column(Integer, nullable=False)

    client_parkings = relationship("ClientParking", back_populates="parking")

class ClientParking(Base):
    __tablename__ = "client_parkings"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    parking_id = Column(Integer, ForeignKey("parkings.id"), nullable=False)
    time_in = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_out = Column(DateTime, nullable=True)

    client = relationship("Client", back_populates="parkings")
    parking = relationship("Parking", back_populates="client_parkings")

    __table_args__ = (
        UniqueConstraint("client_id", "parking_id", name="unique_client_parking"),
    )