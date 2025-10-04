from app.models.user import User
from dep import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.schemas.user import UserIn, UserOut, UserUpdate

router = APIRouter()


@router.post("/user",response_model=UserOut)
async def create_user(user: UserIn, session: SessionDep) :
    user_validate = User.model_validate(user)

    user_similar =session.exec(select(User).where(User.email == user.email)).first()
    if user_similar:
        raise HTTPException(status_code=400, detail="Email already registered")
    session.add(user_validate)
    await session.commit()
    await session.refresh(user_validate)
    return user_validate

@router.get("/user")
async def select_all_user(user: User, session: SessionDep) -> list[User]:
    users=  await session.exec(select(User)).all()

    return users
@router.delete("/user/{id}")
async def delete_user(id: int, session: SessionDep) -> User :
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    await session.commit()
    await session.refresh(user)
    return {"ok": True}

@router.patch("/user/{id}")
async def user_update(id: int, user: UserUpdate, session: SessionDep) -> User :
    user_instance = await session.get(User, id)
    if not user_instance:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    user_instance.sqlmodel.update(user_data)
    session.add(user_instance)
    await session.commit()
    await session.refresh(user_instance)
    return user_instance
