from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    image_url: Optional[str] = None
    price: float
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="items")
