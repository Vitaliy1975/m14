from datetime import date,datetime
from pydantic import BaseModel, Field,EmailStr


class ContactModel(BaseModel):
    """
    ContactModel represents the schema for a contact entity.
    
    Attributes:
        first_name (str): The first name of the contact, with a minimum length of 2 and a maximum length of 25.
        last_name (str): The last name of the contact, with a minimum length of 2 and a maximum length of 25.
        email (EmailStr): The email address of the contact.
        phone_number (int): The phone number of the contact.
        birthday (date): The birth date of the contact.
        additional_data (str): Any additional data related to the contact, with a maximum length of 255.
        user_id (int): The ID of the user associated with the contact, default is None.
    """
    first_name:str=Field(min_length=2,max_length=25)
    last_name:str=Field(min_length=2,max_length=25)
    email:EmailStr
    phone_number:int=Field()
    birthday:date
    additional_data:str=Field(max_length=255)
    user_id:int=Field(default=None)

    class Config:
        # Enables ORM mode for compatibility with ORMs like SQLAlchemy
        orm_mode=True


class ContactResponse(BaseModel):
    """
    ContactResponse represents the schema for a contact response entity.
    
    Attributes:
        id (int): The unique identifier of the contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (EmailStr): The email address of the contact.
        phone_number (int): The phone number of the contact.
        birthday (date): The birth date of the contact.
        additional_data (str): Any additional data related to the contact.
        user_id (int): The ID of the user associated with the contact.
    """
    id:int
    first_name:str
    last_name:str
    email:EmailStr
    phone_number:int
    birthday:date
    additional_data:str
    user_id:int

    class Config:
        # Enables ORM mode for compatibility with ORMs like SQLAlchemy
        orm_mode=True


class UserModel(BaseModel):
    """
    UserModel represents the schema for a user entity.
    
    Attributes:
        username (str): The username of the user, with a minimum length of 2 and a maximum length of 16.
        email (str): The email address of the user.
        password (str): The password of the user, with a minimum length of 6 and a maximum length of 10.
    """
    username: str = Field(min_length=2, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    """
    UserDb represents the schema for a user entity stored in the database.
    
    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        created_at (datetime): The timestamp when the user was created.
        avatar (str): The URL of the user's avatar.
    """
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        # Enables ORM mode for compatibility with ORMs like SQLAlchemy
        orm_mode = True


class UserResponse(BaseModel):
    """
    UserResponse represents the schema for a user response entity.
    
    Attributes:
        user (UserDb): The user data.
        detail (str): A message detailing the response, default is "User successfully created".
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    TokenModel represents the schema for a token entity.
    
    Attributes:
        access_token (str): The access token.
        refresh_token (str): The refresh token.
        token_type (str): The type of the token, default is "bearer".
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    RequestEmail represents the schema for an email request entity.
    
    Attributes:
        email (EmailStr): The email address for the request.
    """
    email: EmailStr
