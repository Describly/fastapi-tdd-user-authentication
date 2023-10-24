from tests.conftest import USER_NAME, USER_EMAIL, USER_PASSWORD

def test_create_user(client):
    data = {
        "name": USER_NAME,
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    }
    response = client.post('/users', json=data)
    assert response.status_code == 201
    assert "password" not in response.json()
    

def test_create_user_with_existing_email(client, inactive_user):
    data = {
        "name": "Keshari Nandan",
        "email": inactive_user.email,
        "password": USER_PASSWORD
    }
    response = client.post("/users/", json=data)
    assert response.status_code != 201


def test_create_user_with_invalid_email(client):
    data = {
        "name": "Keshari Nandan",
        "email": "keshari.com",
        "password": USER_PASSWORD
    }
    response = client.post("/users/", json=data)
    assert response.status_code != 201


def test_create_user_with_empty_password(client):
    data = {
        "name": "Keshari Nandan",
        "email": USER_EMAIL,
        "password": ""
    }
    response = client.post("/users/", json=data)
    assert response.status_code != 201


def test_create_user_with_numeric_password(client):
    data = {
        "name": "Keshari Nandan",
        "email": USER_EMAIL,
        "password": "1232382318763"
    }
    response = client.post("/users/", json=data)
    assert response.status_code != 201


def test_create_user_with_char_password(client):
    data = {
        "name": "Keshari Nandan",
        "email": USER_EMAIL,
        "password": "asjhgahAdF"
    }
    response = client.post("/users/", json=data)
    assert response.status_code != 201


def test_create_user_with_alphanumeric_password(client):
    data = {
        "name": "Keshari Nandan",
        "email": USER_EMAIL,
        "password": "sjdgajhGG27862"
    }
    response = client.post("/users/", json=data)
    assert response.status_code != 201