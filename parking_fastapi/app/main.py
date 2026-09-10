from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db, engine
from . import models, schemas, crud, dependencies

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

@app.post("/client_parkings", response_model=schemas.ClientParking, status_code=201)
def enter_parking(
    record: schemas.ClientParkingCreate,
    db: Session = Depends(get_db),
    _client=Depends(dependencies.get_client_or_404),
    parking=Depends(dependencies.check_parking_available),
):
    dependencies.check_client_not_parked(record.client_id, record.parking_id, db)
    new_record = crud.create_parking_record(db, record)
    parking.count_available_places -= 1
    db.commit()
    db.refresh(parking)
    return new_record

@app.delete("/client_parkings", response_model=schemas.ExitResponse)
def exit_parking(
    record: schemas.ClientParkingCreate,
    db: Session = Depends(get_db),
    client=Depends(dependencies.get_client_or_404),
    parking=Depends(dependencies.get_parking_or_404),
):
    active = crud.get_active_record(db, record.client_id, record.parking_id)
    if not active:
        raise HTTPException(status_code=400, detail="Client is not parked here")

    if not client.credit_card:
        raise HTTPException(status_code=400, detail="No credit card linked")

    amount = 100
    parking.count_available_places += 1
    updated_record = crud.update_parking_record_out(db, active)

    return schemas.ExitResponse(
        message="Exit successful",
        amount_charged=amount,
        record=updated_record
    )
