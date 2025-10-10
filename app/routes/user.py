
# app/routers/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List


# Import models, schemas, and dependencies
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from database import get_session
from security import get_password_hash,get_current_active_user,RoleChecker


#  for role check - this is the name define in database
from app.core.permission import FormName, PermissionAction


# Create an API router for user-related endpoints
router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
        *,
        session: AsyncSession = Depends(get_session),
        user_in: UserCreate,
        _permission_check: None = Depends(RoleChecker(form_name=FormName.USER, required_permission=PermissionAction.INSERT)),
        current_user: User = Depends(get_current_active_user)

):
    """
    Create a new user in the database.
    """
    # Check if a user with the same telegram_id already exists
    db_user = await session.exec(select(User).where(User.telegram_id == user_in.telegram_id))
    if db_user.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this Telegram ID already exists."
        )

    # Check for duplicate national_code
    if user_in.national_code:
        existing_user = await session.exec(select(User).where(User.national_code == user_in.national_code))
        if existing_user.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this national code already exists."
            )

    # Check for duplicate mobile_number
    if user_in.mobile_number:
        existing_user = await session.exec(select(User).where(User.mobile_number == user_in.mobile_number))
        if existing_user.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this mobile number already exists."
            )

    # Hash the plain password from the input schema
    hashed_password = get_password_hash(user_in.password)

    # Create a dictionary of user data, excluding the plain password
    user_data = user_in.model_dump(exclude={"password"})

    # Create the User DB model instance with the hashed password
    db_user_obj = User(**user_data, hashed_password=hashed_password)

    # Add the new user to the session and commit to the database
    session.add(db_user_obj)
    await session.commit()
    await session.refresh(db_user_obj)

    return db_user_obj


@router.get("/{user_id}", response_model=UserRead)
async def read_user_by_id(
        user_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
        _permission_check: None = Depends(RoleChecker(form_name=FormName.USER, required_permission=PermissionAction.VIEW))

):
    """
    Retrieve a user by their ID.
    """
    # Fetch the user from the database by primary key
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )
    return user



@router.get("/", response_model=List[UserRead])
async def read_users(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _permission_check: None = Depends(RoleChecker(form_name=FormName.USER, required_permission=PermissionAction.VIEW))

):
    """
    Retrieve a list of all users.
    """
    users = await session.exec(select(User))
    return users.all()



# app/routers/user.py

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _permission_check: None = Depends(RoleChecker(form_name=FormName.USER, required_permission=PermissionAction.UPDATE))
):
    """
    Update an existing user's information.
    """
    # Retrieve the user by their ID
    user_instance = await session.get(User, user_id)
    if not user_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    # Check for duplicate national_code, mobile_number, or full_name
    if user_in.national_code:
        existing_user = await session.exec(select(User).where(User.national_code == user_in.national_code))
        if existing_user.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this national code already exists."
            )

    if user_in.mobile_number:
        existing_user = await session.exec(select(User).where(User.mobile_number == user_in.mobile_number))
        if existing_user.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this mobile number already exists."
            )


    # update user
    user_data = user_in.model_dump(exclude_unset=True)

    user_instance.sqlmodel_update(user_data)


    # Commit the changes to the database
    session.add(user_instance)
    await session.commit()
    await session.refresh(user_instance)

    return user_instance




@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _permission_check: None = Depends(RoleChecker(form_name=FormName.USER, required_permission=PermissionAction.DELETE))
):
    """
    Delete a user by their ID.
    """
    # Retrieve the user by their ID
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    # Delete the user from the database
    await session.delete(user)
    await session.commit()

    return None
