from typing import List
import datetime

from sqlalchemy.orm import Session

from src.database.models import Contact,User
from src.schemas import ContactModel


# Function to retrieve a list of contacts for a given user, with pagination
async def get_contacts(skip: int, limit: int,user:User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a given user, with pagination.

    Args:
        skip (int): The number of contacts to skip (for pagination).
        limit (int): The maximum number of contacts to return.
        user (User): The user for whom to retrieve the contacts.
        db (Session): The SQLAlchemy database session.

    Returns:
        List[Contact]: A list of Contact objects.
    """
    return db.query(Contact).filter(Contact.user_id==user.id).offset(skip).limit(limit).all()


# Function to retrieve a single contact by ID for a given user
async def get_contact(tag_id: int,user:User, db: Session) -> Contact:
    """
    Retrieves a single contact by ID for a given user.

    Args:
        tag_id (int): The ID of the contact to retrieve.
        user (User): The user for whom to retrieve the contact.
        db (Session): The SQLAlchemy database session.

    Returns:
        Contact: The Contact object, or None if not found.
    """
    return db.query(Contact).filter(Contact.id == tag_id,Contact.user_id==user.id).first()


# Function to create a new contact for a given user
async def create_contact(body: ContactModel, db: Session,user:User) -> Contact:
    """
    Creates a new contact for a given user.

    Args:
        body (ContactModel): The contact data to create.
        db (Session): The SQLAlchemy database session.
        user (User): The user for whom to create the contact.

    Returns:
        Contact: The created Contact object.
    """
    tag = Contact(user_id=user.id,first_name=body.first_name,last_name=body.last_name,email=body.email,phone_number=body.phone_number,birthday=body.birthday,additional_data=body.additional_data)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


# Function to update an existing contact for a given user
async def update_contact(tag_id: int, body: ContactModel, db: Session,user:User) -> Contact | None:
    """
    Updates an existing contact for a given user.

    Args:
        tag_id (int): The ID of the contact to update.
        body (ContactModel): The updated contact data.
        db (Session): The SQLAlchemy database session.
        user (User): The user for whom to update the contact.

    Returns:
        Contact | None: The updated Contact object, or None if the contact was not found.
    """
    tag = db.query(Contact).filter(Contact.id == tag_id,Contact.user_id==user.id).first()
    if tag:
        tag.first_name = body.first_name
        tag.last_name=body.last_name
        tag.email=body.email
        tag.phone_number=body.phone_number
        tag.birthday=body.birthday
        tag.additional_data=body.additional_data
        db.commit()
    return tag


# Function to remove a contact for a given user
async def remove_contact(tag_id: int, db: Session,user:User)  -> Contact | None:
    """
    Removes a contact for a given user.

    Args:
        tag_id (int): The ID of the contact to remove.
        db (Session): The SQLAlchemy database session.
        user (User): The user for whom to remove the contact.

    Returns:
        Contact | None: The removed Contact object, or None if the contact was not found.
    """
    tag = db.query(Contact).filter(Contact.id == tag_id,Contact.user_id==user.id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag


# Function to search for contacts based on various criteria for a given user
async def search_contacts(db: Session,user:User, first_name: str = None, last_name: str = None, email: str = None):
    """
    Searches for contacts based on various criteria for a given user.

    Args:
        db (Session): The SQLAlchemy database session.
        user (User): The user for whom to search the contacts.
        first_name (str, optional): The first name to search for.
        last_name (str, optional): The last name to search for.
        email (str, optional): The email to search for.

    Returns:
        List[Contact] | None: A list of Contact objects matching the search criteria, or None if no contacts were found.
    """
    if first_name and last_name and email:
        return db.query(Contact).filter(Contact.first_name == first_name,Contact.last_name == last_name,Contact.email == email,Contact.user_id==user.id).all()
    elif first_name and last_name:
        return db.query(Contact).filter(Contact.first_name == first_name,Contact.last_name == last_name,Contact.user_id==user.id).all()
    elif last_name and email:
        return db.query(Contact).filter(Contact.last_name == last_name,Contact.email == email,Contact.user_id==user.id).all()
    elif first_name and email:
        return db.query(Contact).filter(Contact.first_name == first_name,Contact.email == email,Contact.user_id==user.id).all()
    elif first_name:
        return db.query(Contact).filter(Contact.first_name == first_name,Contact.user_id==user.id).all()
    elif last_name:
        return db.query(Contact).filter(Contact.last_name == last_name,Contact.user_id==user.id).all()
    elif email:
        return db.query(Contact).filter(Contact.email == email,Contact.user_id==user.id).all()
    return None


# Function to retrieve a list of contacts with birthdays within the next 7 days for a given user
async def birthdays(db: Session,user:User):
    """
    Retrieves a list of contacts with birthdays within the next 7 days for a given user.

    Args:
        db (Session): The SQLAlchemy database session.
        user (User): The user for whom to retrieve the contacts.

    Returns:
        List[Contact]: A list of Contact objects with birthdays within the next 7 days.
    """
    contacts=db.query(Contact).filter(Contact.user_id==user.id).all()
    congratulation_list=[]
    today_date=datetime.datetime.today().date()
    today_year=today_date.year
    today_year_string=str(today_year)
    for contact in contacts:
        birthday_noyear_string=(contact.birthday).strftime("%m.%d")
        birthday_this_year_string=today_year_string+"."+birthday_noyear_string
        birthday_this_year=datetime.datetime.strptime(birthday_this_year_string,"%Y.%m.%d").date()
        difference=birthday_this_year-today_date
        if difference.days<0:
            continue
        elif difference.days>7:
            continue
        else:
            congratulation_list.append(contact)
    return congratulation_list