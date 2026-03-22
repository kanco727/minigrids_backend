from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str


class UserInfo(BaseModel):
    id: int
    email: EmailStr
    role: str
    actif: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo