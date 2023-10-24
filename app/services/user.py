

from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from app.config.security import generate_token, get_token_payload, hash_password, is_password_strong_enough, load_user, str_decode, str_encode, verify_password
from app.models.user import User, UserToken
from app.services.email import send_account_activation_confirmation_email, send_account_verification_email, send_password_reset_email
from app.utils.email_context import FORGOT_PASSWORD, USER_VERIFY_ACCOUNT
from app.utils.string import unique_string
from app.config.settings import get_settings

settings = get_settings()

async def create_user_account(data, session, background_tasks):
    
    user_exist = session.query(User).filter(User.email == data.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="Email is already exists.")
    
    if not is_password_strong_enough(data.password):
        raise HTTPException(status_code=400, detail="Please provide a strong password.")
    
    
    user = User()
    user.name = data.name
    user.email = data.email
    user.password = hash_password(data.password)
    user.is_active = False
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Account Verification Email
    await send_account_verification_email(user, background_tasks=background_tasks)
    return user
    
    
async def activate_user_account(data, session, background_tasks):
    user = session.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="This link is not valid.")
    
    user_token = user.get_context_string(context=USER_VERIFY_ACCOUNT)
    try:
        token_valid = verify_password(user_token, data.token)
    except Exception as verify_exec:
        logging.exception(verify_exec)
        token_valid = False
    if not token_valid:
        raise HTTPException(status_code=400, detail="This link either expired or not valid.")
    
    user.is_active = True
    user.updated_at = datetime.utcnow()
    user.verified_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    # Activation confirmation email
    await send_account_activation_confirmation_email(user, background_tasks)
    return user


async def get_login_token(data, session):
    # verify the email and password
    # Verify that user account is verified
    # Verify user account is active
    # generate access_token and refresh_token and ttl
    
    user = await load_user(data.username, session)
    if not user:
        raise HTTPException(status_code=400, detail="Email is not registered with us.")
    
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password.")
    
    if not user.verified_at:
        raise HTTPException(status_code=400, detail="Your account is not verified. Please check your email inbox to verify your account.")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Your account has been dactivated. Please contact support.")
        
    # Generate the JWT Token
    return _generate_tokens(user, session)


async def get_refresh_token(refresh_token, session):
    token_payload = get_token_payload(refresh_token, settings.SECRET_KEY, settings.JWT_ALGORITHM)
    if not token_payload:
        raise HTTPException(status_code=400, detail="Invalid Request.")
    
    refresh_key = token_payload.get('t')
    access_key = token_payload.get('a')
    user_id = str_decode(token_payload.get('sub'))
    user_token = session.query(UserToken).options(joinedload(UserToken.user)).filter(UserToken.refresh_key == refresh_key,
                                                 UserToken.access_key == access_key,
                                                 UserToken.user_id == user_id,
                                                 UserToken.expires_at > datetime.utcnow()
                                                 ).first()
    if not user_token:
        raise HTTPException(status_code=400, detail="Invalid Request.")
    
    user_token.expires_at = datetime.utcnow()
    session.add(user_token)
    session.commit()
    return _generate_tokens(user_token.user, session)


def _generate_tokens(user, session):
    refresh_key = unique_string(100)
    access_key = unique_string(50)
    rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    user_token = UserToken()
    user_token.user_id = user.id
    user_token.refresh_key = refresh_key
    user_token.access_key = access_key
    user_token.expires_at = datetime.utcnow() + rt_expires
    session.add(user_token)
    session.commit()
    session.refresh(user_token)

    at_payload = {
        "sub": str_encode(str(user.id)),
        'a': access_key,
        'r': str_encode(str(user_token.id)),
        'n': str_encode(f"{user.name}")
    }

    at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = generate_token(at_payload, settings.JWT_SECRET, settings.JWT_ALGORITHM, at_expires)

    rt_payload = {"sub": str_encode(str(user.id)), "t": refresh_key, 'a': access_key}
    refresh_token = generate_token(rt_payload, settings.SECRET_KEY, settings.JWT_ALGORITHM, rt_expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": at_expires.seconds
    }
    
async def email_forgot_password_link(data, background_tasks, session):
    user = await load_user(data.email, session)
    if not user.verified_at:
        raise HTTPException(status_code=400, detail="Your account is not verified. Please check your email inbox to verify your account.")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Your account has been dactivated. Please contact support.")
    
    await send_password_reset_email(user, background_tasks)
    
    
async def reset_user_password(data, session):
    user = await load_user(data.email, session)
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")
        
    
    if not user.verified_at:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    user_token = user.get_context_string(context=FORGOT_PASSWORD)
    try:
        token_valid = verify_password(user_token, data.token)
    except Exception as verify_exec:
        logging.exception(verify_exec)
        token_valid = False
    if not token_valid:
        raise HTTPException(status_code=400, detail="Invalid window.")
    
    user.password = hash_password(data.password)
    user.updated_at = datetime.now()
    session.add(user)
    session.commit()
    session.refresh(user)
    # Notify user that password has been updated
    
    
async def fetch_user_detail(pk, session):
    user = session.query(User).filter(User.id == pk).first()
    if user:
        return user
    raise HTTPException(status_code=400, detail="User does not exists.")