""" Message model tests """

import os
from unittest import TestCase
from sqlalchemy import exc

from app import app
from models import db, User, Message

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
db.create_all()

class MessageModelTestCase(TestCase):
    """ Test message model """

    def setUp(self):
        """ set up sample data """

        db.drop_all()
        db.create_all()

        u1=User.signup("testuser", "testuser@gmail.com", "pass", None)
        db.session.commit()

        self.u1=u1
        self.u1_id = u1.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_create_message(self):
        """ test creating message """

        message = Message(text='test text',user_id= self.u1.id)

        self.assertIsNotNone(message)

    def test_message_user(self):
        """ Test message is connected to user """
        message = Message(text='test text',user_id= self.u1.id)

        self.assertIsNotNone(message)

        db.session.add(message)
        db.session.commit()

        user = User.query.get(self.u1.id)
        self.assertEqual(message.id,user.messages[0].id)
        self.assertEqual('test text',user.messages[0].text)

    def test_delete_cascade(self):
        """test delete message """
        message = Message(text='test text',user_id= self.u1.id)
        db.session.add(message)
        db.session.commit()

        db.session.delete(self.u1)
        db.session.commit()

        self.assertIsNone(Message.query.get(message.id))
        
