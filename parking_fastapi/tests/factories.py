import factory
from factory import Faker, LazyAttribute, Maybe
from app.models import Client, Parking
from tests.conftest import TestingSessionLocal


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    
    class Meta:
        model = Client
        sqlalchemy_session = TestingSessionLocal()

    name = Faker("first_name")
    surname = Faker("last_name")
    credit_card = Maybe(
        "yes",
        yes_declaration=Faker("credit_card_number"),
        no_declaration=None,
    )
    car_number = Faker("license_plate")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = Parking
        sqlalchemy_session = TestingSessionLocal()

    address = Faker("street_address")
    opened = Faker("boolean")
    count_places = Faker("random_int", min=1, max=100)
    count_available_places = LazyAttribute(lambda o: o.count_places)
