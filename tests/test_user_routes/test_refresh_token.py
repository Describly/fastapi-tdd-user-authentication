"""
1. User shoud be able to generate the login token with valid refresh token.
2. User should not be able to generate login token with invalid refresh token.
.....
"""

import logging
from app.services.user import _generate_tokens


def test_refresh_token(client, user, test_session):
    data = _generate_tokens(user, test_session)
    header = {
        "refresh-token": data['refresh_token']
    }
    response = client.post("/auth/refresh", json={}, headers=header)
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()
    
def test_refresh_token_with_invalid_token(client, user, test_session):
    data = _generate_tokens(user, test_session)
    header = {
        "refresh-token": 'sakdhasjkdhahdjkahdjka'
    }
    response = client.post("/auth/refresh", json={}, headers=header)
    assert response.status_code == 400
    assert 'access_token' not in response.json()
    assert 'refresh_token' not in response.json()