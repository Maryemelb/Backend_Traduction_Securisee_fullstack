
from pydantic import BaseModel

class Description(BaseModel):
    text: str
    choice: str
    