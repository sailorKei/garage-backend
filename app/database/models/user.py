from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .item import Item  # Import uniquement pour l'auto-complétion

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    email: str
    password: str
    photo_name: Optional[str] = None
    role: str

    items: List["Item"] = Relationship(back_populates="user")
