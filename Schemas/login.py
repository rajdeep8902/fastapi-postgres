from pydantic import BaseModel, Field

class LoginBody(BaseModel):
    username: str
    password: str