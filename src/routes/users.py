from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb


# Create a router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve the current user's information.

    Args:
        current_user (User): The authenticated user, obtained from the auth_service.

    Returns:
        User: The current user's information.
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),db: Session = Depends(get_db)):
    """
    Update the avatar of the current user.

    Args:
        file (UploadFile): The image file to be used as the new avatar.
        current_user (User): The authenticated user, obtained from the auth_service.
        db (Session): The database session.

    Returns:
        User: The updated user information with the new avatar URL.
    """
    # Configure Cloudinary with the necessary credentials
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    
    # Upload the file to Cloudinary
    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)

    # Generate the URL for the uploaded image with specific dimensions
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}').build_url(width=250, height=250, crop='fill', version=r.get('version'))

    # Update the user's avatar in the database
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
