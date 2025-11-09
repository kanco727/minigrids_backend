from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
