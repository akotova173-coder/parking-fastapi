import pytest
from app.models import Client, Parking
from tests.factories import ClientFactory, ParkingFactory


@pytest.mark.parametrize("route", ["/", "/clients", "/clients/1"])
def test_get_routes(client, route):
    response = client.get(route)
    assert response.status_code == 200


def test_create_client(client, db_session):
    data = {
        "name": "Анна",
        "surname": "Сидорова",
        "credit_card": "9876543210987654",
        "car_number": "B456DE"
    }
    response = client.post("/clients", json=data)
    assert response.status_code == 201
    resp_json = response.json()
    assert resp_json["name"] == "Анна"
    assert resp_json["id"] is not None

    new_client = db_session.query(Client).filter(Client.id == resp_json["id"]).first()
    assert new_client is not None
    assert new_client.credit_card == "9876543210987654"


def test_create_parking(client, db_session):
    data = {
        "address": "ул. Парковая, 10",
        "count_places": 20,
        "opened": True
    }
    response = client.post("/parkings", json=data)
    assert response.status_code == 201
    resp_json = response.json()
    assert resp_json["address"] == "ул. Парковая, 10"
    assert resp_json["count_places"] == 20
    assert resp_json["count_available_places"] == 20

    parking = db_session.query(Parking).filter(Parking.id == resp_json["id"]).first()
    assert parking is not None


def test_create_client_with_factory(client, db_session):
    ClientFactory._meta.sqlalchemy_session = db_session
    old_count = db_session.query(Client).count()
    new_client = ClientFactory()
    db_session.commit()

    assert new_client.id is not None
    assert new_client.name is not None
    assert new_client.surname is not None
    assert new_client.credit_card is None or isinstance(new_client.credit_card, str)
    assert new_client.car_number is not None

    new_count = db_session.query(Client).count()
    assert new_count == old_count + 1


def test_create_parking_with_factory(client, db_session):
    ParkingFactory._meta.sqlalchemy_session = db_session
    old_count = db_session.query(Parking).count()
    new_parking = ParkingFactory()
    db_session.commit()

    assert new_parking.id is not None
    assert new_parking.address is not None
    assert new_parking.count_places > 0
    assert new_parking.count_available_places == new_parking.count_places
    assert new_parking.opened in (True, False)

    new_count = db_session.query(Parking).count()
    assert new_count == old_count + 1


def test_enter_parking(client):
    app_state = client.app.state
    client_id = app_state.client_id
    parking_id = app_state.parking_id

    response = client.post(
        "/client_parkings",
        json={"client_id": client_id,
              "parking_id": parking_id}
    )
    assert response.status_code == 201
    resp_json = response.json()
    assert resp_json["client_id"] == client_id
    assert resp_json["parking_id"] == parking_id
    assert resp_json["time_out"] is None

    parking_resp = client.get(f"/parkings/{parking_id}")
    assert parking_resp.json()["count_available_places"] == 4


def test_exit_parking(client):
    app_state = client.app.state
    client_id = app_state.client_id
    parking_id = app_state.parking_id

    enter = client.post(
        "/client_parkings",
        json={"client_id": client_id,
              "parking_id": parking_id}
    )
    assert enter.status_code == 201

    exit_resp = client.delete(f"/client_parkings?client_id={client_id}&parking_id={parking_id}")
    assert exit_resp.status_code == 200
    exit_json = exit_resp.json()
    assert exit_json["message"] == "Exit successful"
    assert exit_json["amount_charged"] == 100
    assert exit_json["record"]["time_out"] is not None

    parking_resp = client.get(f"/parkings/{parking_id}")
    assert parking_resp.json()["count_available_places"] == 5

    @pytest.mark.parametrize("closed, expected_code", [(False, 400), (True, 400)])
    def test_enter_parking_closed_or_no_places(client, db_session, closed):
        data = {
            "address": "Тестовая",
            "count_places": 10 if not closed else 0,
            "opened": not closed
        }
        if closed:
            # закрытая
            data["opened"] = False
            data["count_places"] = 10
        else:
            data["opened"] = True
            data["count_places"] = 0
        resp = client.post("/parkings", json=data)
        assert resp.status_code == 201
        parking_id = resp.json()["id"]

        client_id = client.app.state.client_id
        response = client.post(
            "/client_parkings", 
            json={"client_id": client_id, "parking_id": parking_id}
        )
        assert response.status_code == 400
        if closed:
            assert response.json()["detail"] == "Parking is closed"
        else:
            assert response.json()["detail"] == "No available places"

    def test_exit_parking_no_card(client, db_session):
        app_state = client.app.state
        no_card_client = Client(name="Без", surname="Карты", credit_card=None, car_number="C789FG")
        db_session.add(no_card_client)
        db_session.commit()

        enter = client.post("/client_parkings",
                            json={"client_id": 
                                  no_card_client.id, 
                                  "parking_id": app_state.parking_id})
        assert enter.status_code == 201

        exit_resp = client.delete("/client_parkings",
                                  json={"client_id": 
                                        no_card_client.id, 
                                        "parking_id": app_state.parking_id})
        assert exit_resp.status_code == 400
        assert exit_resp.json()["detail"] == "No credit card linked"

    def test_exit_parking_not_parked(client, db_session):
        new_client = Client(
            name="Новый",
            surname="Клиент",
            credit_card="1111222233334444",
            car_number="D123EF")
        db_session.add(new_client)
        db_session.commit()

        response = client.delete("/client_parkings",
                                 json={"client_id": 
                                       new_client.id, 
                                       "parking_id": client.app.state.parking_id}
                                )
        assert response.status_code == 400
        assert response.json()["detail"] == "Client is not parked here"
