from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .item import Item  # important pour le typage

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    email: str
    password: str
    photo_name: Optional[str] = None
    role: str

    items: List["Item"] = Relationship(back_populates="user")
