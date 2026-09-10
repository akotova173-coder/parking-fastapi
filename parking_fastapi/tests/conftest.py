import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import Client, Parking, ClientParking
from datetime import datetime, timedelta
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")

def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")

def client(db_session):
    client_obj = Client(
        name="Иван",
        surname="Петров",
        credit_card="1234567890123456",
        car_number="A123BC"
    )
    db_session.add(client_obj)
    db_session.flush()

    parking = Parking(
        address="ул. Тестовая, 1",
        count_places=5,
        count_available_places=5,
        opened=True
    )
    db_session.add(parking)
    db_session.flush()

    log = ClientParking(
        client_id=client_obj.id,
        parking_id=parking.id,
        time_in=datetime.utcnow() - timedelta(hours=2),
        time_out=datetime.utcnow() - timedelta(hours=1)
    )
    db_session.add(log)
    db_session.commit()

    app.state.client_id = client_obj.id
    app.state.parking_id = parking.id

    with TestClient(app) as test_client:
        yield test_client
