from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str
    age: int
    
class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: int

class UserUpdate(UserBase):
    email: str | None = None
    username: str | None = None
    age: int | None = None