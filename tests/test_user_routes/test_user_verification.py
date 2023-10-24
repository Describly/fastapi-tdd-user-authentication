"""
1 - Test if the user account action is working
2 - Test activation link valid only once
3 - Test activation is not allowing invalid token
4 - Test activation is not allowining invalid email
"""
import time
from app.config.security import hash_password
from app.models.user import User
from app.utils.email_context import USER_VERIFY_ACCOUNT


def test_user_account_verification(client, inactive_user, test_session):
    token_context = inactive_user.get_context_string(USER_VERIFY_ACCOUNT)
    token = hash_password(token_context)
    data = {
        "email": inactive_user.email,
        "token": token
    }
    response = client.post('/users/verify', json=data)
    assert response.status_code == 200
    activated_user = test_session.query(User).filter(User.email == inactive_user.email).first()
    assert activated_user.is_active is True
    assert activated_user.verified_at is not None


def test_user_link_doesnot_work_twice(client, inactive_user, test_session):
    token_context = inactive_user.get_context_string(USER_VERIFY_ACCOUNT)
    token = hash_password(token_context)
    time.sleep(1)
    data = {
        "email": inactive_user.email,
        "token": token
    }
    response = client.post('/users/verify', json=data)
    assert response.status_code == 200
    ## Account is activated now, let make another call to check if that works, 
    # it should not work though
    response = client.post('/users/verify', json=data)
    assert response.status_code != 200
    
    
def test_user_invalid_token_does_not_work(client, inactive_user, test_session):
    data = {
        "email": inactive_user.email,
        "token": "aksdajskdhakhdjkadhakjdhjahdjka"
    }
    response = client.post('/users/verify', json=data)
    assert response.status_code != 200
    activated_user = test_session.query(User).filter(User.email == inactive_user.email).first()
    assert activated_user.is_active is False
    assert activated_user.verified_at is None
    
def test_user_invalid_email_does_not_work(client, inactive_user, test_session):
    token_context = inactive_user.get_context_string(USER_VERIFY_ACCOUNT)
    token = hash_password(token_context)
    data = {
        "email": "nandan@describly.com",
        "token": token
    }
    response = client.post('/users/verify', json=data)
    assert response.status_code != 200
    activated_user = test_session.query(User).filter(User.email == inactive_user.email).first()
    assert activated_user.is_active is False
    assert activated_user.verified_at is None

    