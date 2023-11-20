from app import schemas


def test_root(client, session):
    response = client.get("/")
    print(response.json().get('message'))
    assert response.json().get('message') == "Hello World"
    assert response.status_code == 200


def test_create_user(client):
    response = client.post("/users/", json={"email": "michael@gmail.com", "password": "password123"})
    new_user = schemas.UserResponse(**response.json())
    assert new_user.email == "michael@gmail.com"
    assert response.status_code == 201




