

from pydantic import BaseModel, EmailStr


class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    
    
class VerifyUserRequest(BaseModel):
    token: str
    email: EmailStr
    
class EmailRequest(BaseModel):
    email: EmailStr
    
class ResetRequest(BaseModel):
    token: str
    email: EmailStr
    password: str
    