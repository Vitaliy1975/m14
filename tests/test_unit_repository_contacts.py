import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
import datetime

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
    search_contacts,
    birthdays
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        notes = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = notes
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, notes)

    async def test_get_contact_found(self):
        note = Contact()
        self.session.query().filter().first.return_value = note
        result = await get_contact(tag_id=1, user=self.user, db=self.session)
        self.assertEqual(result, note)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(tag_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(first_name="test_name", last_name="test_last_name",email="test@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1)
        self.session.query().filter().all.return_value = body
        result = await create_contact(body=body,db=self.session,user=self.user)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email,body.email)
        self.assertEqual(result.phone_number,body.phone_number)
        self.assertEqual(result.birthday,body.birthday)
        self.assertEqual(result.additional_data,body.additional_data)

    async def test_remove_contact_found(self):
        note = Contact()
        self.session.query().filter().first.return_value = note
        result = await remove_contact(tag_id=1, db=self.session,user=self.user)
        self.assertEqual(result, note)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(tag_id=1, db=self.session,user=self.user)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body =ContactModel(first_name="test_name", last_name="test_last_name",email="test@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1)
        self.session.query().filter().first.return_value = body
        # self.session.commit.return_value = None
        result = await update_contact(tag_id=1, body=body,db=self.session,user=self.user)
        self.assertEqual(result, body)

    async def test_update_contact_not_found(self):
        body =ContactModel(first_name="test_name", last_name="test_last_name",email="test@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1)
        self.session.query().filter().first.return_value = None
        # self.session.commit.return_value = None
        result = await update_contact(tag_id=1, body=body, db=self.session,user=self.user)
        self.assertIsNone(result)

    async def test_search_contacts(self):
        contacts=[ContactModel(first_name="test_name1", last_name="test_last_name",email="test@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1),
                  ContactModel(first_name="test_name", last_name="test_last_name1",email="test@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1),
                  ContactModel(first_name="test_name", last_name="test_last_name",email="test1@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1)
                  ]
        self.session.query().filter().all.return_value=contacts
        result=await search_contacts(db=self.session,user=self.user,first_name="test_name1",last_name="test_last_name1",email="test1@example.com")
        self.assertEqual(result,contacts)

    async def test_birthdays(self):
        contacts=[ContactModel(first_name="test_name1", last_name="test_last_name",email="test@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1),
                  ContactModel(first_name="test_name", last_name="test_last_name1",email="test@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1),
                  ContactModel(first_name="test_name", last_name="test_last_name",email="test1@example.com",phone_number=12345,birthday=(datetime.datetime.now().date()-datetime.timedelta(weeks=(52*30))-datetime.timedelta(days=35)),additional_data="test_data",user_id=1)
                  ]
        self.session.query().filter().all.return_value=contacts
        result=await birthdays(db=self.session,user=self.user)
        self.assertEqual(result,contacts)


if __name__ == '__main__':
    unittest.main()

