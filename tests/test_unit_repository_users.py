import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
import datetime

from src.database.models import User
from src.schemas import ContactModel,UserModel
from src.repository.users import get_user_by_email,create_user,update_token,confirmed_email,update_avatar


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session=MagicMock(spec=Session)
        self.user=User(id=1)

    async def test_get_user_by_email_found(self):
        user=User()
        self.session.query().filter().first.return_value=user
        result=await get_user_by_email(email="test@example.com",db=self.session)
        self.assertEqual(result,user)
    
    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value=None
        result=await get_user_by_email(email="test@example.com",db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body=UserModel(username="test_name",email="test@example.com",password="test_passw")
        self.session.query().filter().all.return_value=body
        result=await create_user(body=body,db=self.session)
        self.assertEqual(result.username,body.username)
        self.assertEqual(result.email,body.email)
        self.assertEqual(result.password,body.password)

    async def test_update_avatar(self):
        user=User()
        self.session.query().filter().first.return_value=user
        result=await update_avatar(email="test@example.com",url="url",db=self.session)
        self.assertEqual(result,user)

if __name__=="__main__":
    unittest.main()