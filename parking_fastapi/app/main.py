from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db, engine
from . import models, schemas, crud, dependencies
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Parking API", version="1.0")

@app.get("/")
def root():
    return {"message": "Parking API is running"}

@app.get("/clients", response_model=list[schemas.Client])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_clients(db, skip=skip, limit=limit)

@app.get("/clients/{client_id}", response_model=schemas.Client)
def get_client(client: schemas.Client = Depends(dependencies.get_client_or_404)):
    return client

@app.post("/clients", response_model=schemas.Client, status_code=201)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(db, client)

@app.post("/parkings", response_model=schemas.Parking, status_code=201)
def create_parking(parking: schemas.ParkingCreate, db: Session = Depends(get_db)):
    return crud.create_parking(db, parking)

@app.get("/parkings/{parking_id}", response_model=schemas.Parking)
def get_parking(
    parking_id: int,
    db: Session = Depends(get_db),
):
    parking = crud.get_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    return parking

@app.post("/client_parkings", response_model=schemas.ClientParking, status_code=201)
def enter_parking(
    record: schemas.ClientParkingCreate,
    db: Session = Depends(get_db),
):
    client = crud.get_client(db, record.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    parking = crud.get_parking(db, record.parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")

    if not parking.opened:
        raise HTTPException(status_code=400, detail="Parking is closed")
    if parking.count_available_places <= 0:
        raise HTTPException(status_code=400, detail="No available places")

    active = crud.get_active_record(db, record.client_id, record.parking_id)
    if active:
        raise HTTPException(status_code=400, detail="Client is already parked here")

    existing_record = db.query(models.ClientParking).filter_by(
        client_id=record.client_id,
        parking_id=record.parking_id
    ).first()

    if existing_record:
        existing_record.time_in = datetime.utcnow()
        existing_record.time_out = None
        db_record = existing_record
    else:
        db_record = models.ClientParking(**record.model_dump())
        db.add(db_record)

    parking.count_available_places -= 1
    db.commit()
    db.refresh(parking)
    db.refresh(db_record)
    
    return db_record

@app.delete("/client_parkings", response_model=schemas.ExitResponse)
def exit_parking(
    client_id: int,
    parking_id: int,
    db: Session = Depends(get_db),
):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    parking = crud.get_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")

    active = crud.get_active_record(db, client_id, parking_id)
    if not active:
        raise HTTPException(status_code=400, detail="Client is not parked here")

    if not client.credit_card:
        raise HTTPException(status_code=400, detail="No credit card linked")

    amount = 100
    parking.count_available_places += 1
    active.time_out = datetime.utcnow()
    db.commit()
    db.refresh(active)

    return schemas.ExitResponse(
        message="Exit successful",
        amount_charged=amount,
        record=active
    )
