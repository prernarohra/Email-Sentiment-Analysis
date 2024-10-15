from pydantic import BaseModel

from datetime import datetime


class Email(BaseModel):
    content: str
    created_date: datetime 
    sentiment : str

    class Config:
        orm_mode = True

class EmailOut(Email):
    id: int
    is_deleted: bool
