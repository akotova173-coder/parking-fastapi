from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from . import crud, schemas

def get_client_or_404(client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

def get_parking_or_404(parking_id: int, db: Session = Depends(get_db)):
    parking = crud.get_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    return parking

def check_parking_available(parking=Depends(get_parking_or_404)):
    if not parking.opened:
        raise HTTPException(status_code=400, detail="Parking is closed")
    if parking.count_available_places <= 0:
        raise HTTPException(status_code=400, detail="No available places")
    return parking

def check_client_not_parked(client_id: int, parking_id: int, db: Session = Depends(get_db)):
    active = crud.get_active_record(db, client_id, parking_id)
    if active:
        raise HTTPException(status_code=400, detail="Client is already parked here")
    return active