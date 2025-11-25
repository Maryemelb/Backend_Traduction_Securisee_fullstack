from pydantic import BaseModel

class User_schema(BaseModel):
    username: str
    password: str
    