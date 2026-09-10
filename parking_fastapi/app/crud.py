from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas


def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()


def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_parking(db: Session, parking_id: int):
    return db.query(models.Parking).filter(models.Parking.id == parking_id).first()


def create_parking(db: Session, parking: schemas.ParkingCreate):
    db_parking = models.Parking(
        **parking.model_dump(),
        count_available_places=parking.count_places
    )
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking


def get_active_record(db: Session, client_id: int, parking_id: int):
    return db.query(models.ClientParking).filter(
        models.ClientParking.client_id == client_id,
        models.ClientParking.parking_id == parking_id,
        models.ClientParking.time_out.is_(None)
    ).first()


def create_parking_record(db: Session, record: schemas.ClientParkingCreate):
    db_record = models.ClientParking(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_parking_record_out(db: Session, record: models.ClientParking):
    record.time_out = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record
