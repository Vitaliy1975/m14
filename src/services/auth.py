from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.repository import users as repository_users

import pickle
import redis


class Auth:
    """
    A class for handling authentication-related operations.
    """
    # Initialize password hashing context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Load secret key and algorithm from settings
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm

    # Set up OAuth2 scheme for token-based authentication
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    # Initialize Redis connection
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)


    def verify_password(self, plain_password, hashed_password):
        """
        Verify if the plain password matches the hashed password.

        :param plain_password: The password in plain text
        :param hashed_password: The hashed password to compare against
        :return: True if the password is correct, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)


    def get_password_hash(self, password: str):
        """
        Generate a hash for the given password.

        :param password: The password to hash
        :return: The hashed password
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a new access token.

        :param data: The data to encode in the token
        :param expires_delta: Optional expiration time in seconds
        :return: The encoded access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a new refresh token.

        :param data: The data to encode in the token
        :param expires_delta: Optional expiration time in seconds
        :return: The encoded refresh token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token


    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode and validate a refresh token.

        :param refresh_token: The refresh token to decode
        :return: The email associated with the token
        :raises HTTPException: If the token is invalid or expired
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
        

    def create_email_token(self, data: dict):
        """
        Create a token for email verification.

        :param data: The data to encode in the token
        :return: The encoded email token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token


    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Get the current user based on the provided token.

        :param token: The access token
        :param db: The database session
        :return: The current user
        :raises HTTPException: If the token is invalid or the user is not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        
        # Try to get user from Redis cache
        user = self.r.get(f"user:{email}")
        if user is None:
            # If not in cache, get from database
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            # Cache user data in Redis
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user
    

    async def get_email_from_token(self, token: str):
        """
        Extract the email from a token.

        :param token: The token to decode
        :return: The email associated with the token
        :raises HTTPException: If the token is invalid
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="Invalid token for email verification")


# Create an instance of the Auth class
auth_service = Auth()
