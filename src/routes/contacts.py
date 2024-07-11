from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel,ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

# Create an APIRouter instance for contacts
router = APIRouter(prefix='/contacts', tags=["contacts"])


# Define a GET endpoint to read all contacts
# This endpoint is rate-limited to 10 requests per minute
@router.get("/", response_model=List[ContactResponse],description='No more than 10 requests per minute',dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user:User=Depends(auth_service.get_current_user)):
    """
    Retrieve a list of contacts.

    Args:
        skip (int, optional): The number of contacts to skip. Defaults to 0.
        limit (int, optional): The maximum number of contacts to return. Defaults to 100.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        List[ContactResponse]: A list of contact responses.

    Raises:
        HTTPException: If an error occurs.
    """
    tags = await repository_contacts.get_contacts(skip, limit,current_user,db)
    return tags


# Define a GET endpoint to read a specific contact by ID
# This endpoint is rate-limited to 10 requests per minute
@router.get("/{tag_id}", response_model=ContactResponse,description='No more than 10 requests per minute',dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contact(tag_id: int, db: Session = Depends(get_db),current_user:User=Depends(auth_service.get_current_user)):
    """
    Retrieve a specific contact by ID.

    Args:
        tag_id (int): The ID of the contact to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        ContactResponse: The contact response.

    Raises:
        HTTPException: If the contact is not found.
    """
    tag = await repository_contacts.get_contact(tag_id,current_user,db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return tag

# Define a POST endpoint to create a new contact
# This endpoint is rate-limited to 2 requests per minute
@router.post("/", response_model=ContactResponse,description='No more than 2 requests per minute',dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def create_contact(body: ContactModel,db: Session = Depends(get_db),current_user:User=Depends(auth_service.get_current_user)):
    """
    Create a new contact.

    Args:
        body (ContactModel): The contact data to create.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        ContactResponse: The created contact response.

    Raises:
        HTTPException: If an error occurs.
    """
    return await repository_contacts.create_contact(body,db,current_user)


# Define a PUT endpoint to update an existing contact
# This endpoint is rate-limited to 10 requests per minute
@router.put("/{tag_id}", response_model=ContactResponse,description='No more than 10 requests per minute',dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactModel, tag_id: int, db: Session = Depends(get_db),current_user:User=Depends(auth_service.get_current_user)):
    """
    Update an existing contact.

    Args:
        body (ContactModel): The contact data to update.
        tag_id (int): The ID of the contact to update.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        ContactResponse: The updated contact response.

    Raises:
        HTTPException: If the contact is not found.
    """
    tag = await repository_contacts.update_contact(tag_id,body,db,current_user)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return tag


# Define a DELETE endpoint to delete a contact
# This endpoint is rate-limited to 10 requests per minute
@router.delete("/{tag_id}", response_model=ContactResponse,description='No more than 10 requests per minute',dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_contact(tag_id: int, db: Session = Depends(get_db),current_user:User=Depends(auth_service.get_current_user)):
    """
    Delete a contact.

    Args:
        tag_id (int): The ID of the contact to delete.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        ContactResponse: The deleted contact response.

    Raises:
        HTTPException: If the contact is not found.
    """
    tag = await repository_contacts.remove_contact(tag_id,db,current_user)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return tag


# Define a GET endpoint to search for contacts
# This endpoint is rate-limited to 10 requests per minute
@router.get("/find/",response_model=List[ContactResponse],description='No more than 10 requests per minute',dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def find_contacts(first_name:str=None,last_name:str=None,email:str=None,db:Session=Depends(get_db),current_user:User=Depends(auth_service.get_current_user)):
    """
    Search for contacts by first name, last name, or email.

    Args:
        first_name (str, optional): The first name to search for. Defaults to None.
        last_name (str, optional): The last name to search for. Defaults to None.
        email (str, optional): The email to search for. Defaults to None.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        List[ContactResponse]: A list of contact responses matching the search criteria.

    Raises:
        HTTPException: If no contacts are found.
    """
    result=await repository_contacts.search_contacts(db,current_user,first_name,last_name,email)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Contact not found")
    return result


# Define a GET endpoint to retrieve contacts with upcoming birthdays
# This endpoint is rate-limited to 10 requests per minute
@router.get("/birthday/",response_model=List[ContactResponse],description='No more than 10 requests per minute',dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def birth_contacts(db:Session=Depends(get_db),current_user:User=Depends(auth_service.get_current_user)):
    """
    Retrieve contacts with upcoming birthdays.

    Args:
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        List[ContactResponse]: A list of contact responses with upcoming birthdays.

    Raises:
        HTTPException: If no contacts with upcoming birthdays are found.
    """
    result=await repository_contacts.birthdays(db,current_user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Contact not found")
    return result