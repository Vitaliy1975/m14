from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


# Function to get a user by their email address
async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user from the database based on their email address.

    Args:
        email (str): The email address of the user to retrieve.
        db (Session): The SQLAlchemy database session.

    Returns:
        User: The user object, or None if the user is not found.
    """
    return db.query(User).filter(User.email == email).first()


# Function to create a new user
async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user in the database.

    Args:
        body (UserModel): The user data to be used for creating the new user.
        db (Session): The SQLAlchemy database session.

    Returns:
        User: The newly created user object.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(email=body.email,username=body.username,password=body.password,avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Function to update a user's refresh token
async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token for a user.

    Args:
        user (User): The user object to update.
        token (str | None): The new refresh token value, or None to clear the token.
        db (Session): The SQLAlchemy database session.
    """
    user.refresh_token = token
    db.commit()


# Function to mark a user's email as confirmed
async def confirmed_email(email: str, db: Session) -> None:
    """
    Marks a user's email as confirmed in the database.

    Args:
        email (str): The email address of the user to confirm.
        db (Session): The SQLAlchemy database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


# Function to update a user's avatar
async def update_avatar(email, url: str, db: Session) -> User:
    """
    Updates a user's avatar image in the database.

    Args:
        email (str): The email address of the user to update.
        url (str): The URL of the new avatar image.
        db (Session): The SQLAlchemy database session.

    Returns:
        User: The updated user object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
