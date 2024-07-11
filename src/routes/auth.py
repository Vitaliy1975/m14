from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail

from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email


# Create an APIRouter instance with the prefix '/auth' and the tag 'auth'
router = APIRouter(prefix='/auth', tags=["auth"])

# Create an HTTPBearer instance for authentication
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Sign up a new user.

    Args:
        body (UserModel): The user data to be registered.
        background_tasks (BackgroundTasks): A FastAPI dependency to run tasks in the background.
        request (Request): The current HTTP request.
        db (Session): The database session.

    Returns:
        UserResponse: The response containing the newly created user and a success message.
    """
    # Check if the user already exists
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    
    # Hash the password
    body.password = auth_service.get_password_hash(body.password)

    # Create a new user
    new_user = await repository_users.create_user(body, db)

    # Send a confirmation email in the background
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Log in a user and generate access and refresh tokens.

    Args:
        body (OAuth2PasswordRequestForm): The login credentials.
        db (Session): The database session.

    Returns:
        TokenModel: The response containing the access and refresh tokens.
    """
    # Get the user by email
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    
    # Check if the user's email is confirmed
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    
    # Verify the password
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    # Generate access and refresh tokens
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})

    # Update the user's refresh token
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refresh the access token using the refresh token.

    Args:
        credentials (HTTPAuthorizationCredentials): The authorization credentials.
        db (Session): The database session.

    Returns:
        TokenModel: The response containing the new access and refresh tokens.
    """
    # Get the refresh token from the credentials
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    
    # Get the user by email
    user = await repository_users.get_user_by_email(email, db)

    # Verify the refresh token
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    # Generate new access and refresh tokens
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})

    # Update the user's refresh token
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm the user's email using the provided token.

    Args:
        token (str): The token used to confirm the email.
        db (Session): The database session.

    Returns:
        dict: A message indicating the email confirmation status.
    """
    # Get the email from the token
    email = await auth_service.get_email_from_token(token)

    # Get the user by email
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    
    # Check if the email is already confirmed
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    
    # Confirm the user's email
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,db: Session = Depends(get_db)):
    """
    Request a confirmation email to be sent to the user.

    Args:
        body (RequestEmail): The email to be confirmed.
        background_tasks (BackgroundTasks): A FastAPI dependency to run tasks in the background.
        request (Request): The current HTTP request.
        db (Session): The database session.

    Returns:
        dict: A message indicating that the confirmation email has been sent.
    """
    # Get the user by email
    user = await repository_users.get_user_by_email(body.email, db)

    # Check if the email is already confirmed
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    
    # Send the confirmation email in the background
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
