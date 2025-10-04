from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel
from database import get_session

SessionDep = Annotated[Session, Depends(get_session)]




