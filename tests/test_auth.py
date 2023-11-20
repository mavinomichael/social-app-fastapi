import pytest
from app import schemas
from jose import jwt
from app.config import settings


def test_login_user(client, test_user):
    response = client.post('/login', data={"username": test_user['email'], "password": test_user['password']})
    print(response.json())
    login_res = schemas.Token(**response.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=settings.algorithm)
    id = str(payload.get("user_id"))
    assert int(id) == test_user['id']
    assert login_res.token_type == "bearer"
    assert response.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('michael@gmail.com', 'wrongPassword', 403),
    ('wrongemail@gmail.com', 'wrongPassword', 403),
    (None, 'password123', 422),
    ('wrongemail@gmail.com', None, 422),
])
def test_incorrect_login(test_user, client, email, password, status_code):
    response = client.post("/login", data={"username": email, "password": password})
    assert response.status_code == status_code
