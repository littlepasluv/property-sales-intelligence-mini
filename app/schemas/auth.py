from pydantic import BaseModel

class LoginRequest(BaseModel):
    persona: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
