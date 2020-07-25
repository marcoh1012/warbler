"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1","test1@test.com","pass",None)
        u2 = User.signup("test2","test2@test.com","pass",None)
        db.session.commit()

        self.u1=u1
        self.u1_id = u1.id

        self.u2=u2
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    # def test_repr(self):
    #     """ Test repr method """

    #     repr = f"<User #None: testuser, test@test.com>"
    #     self.assertEqual(repr, u2)

    def test_user_follows(self):
        """ test user follows another user """

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.following),1)
        self.assertEqual(len(self.u2.following),0)

        self.assertEqual(self.u1.following[0].id,self.u2.id)
        self.assertEqual(self.u2.followers[0].id,self.u1.id)

    def test_is_following(self):
        """ Test is following method """

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        """ Test is followed by method """

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))
        

    def test_signup(self):
        "test user can sign up"

        new_user = User.signup('testuser',"testuser@gmail.com","password",None)
        db.session.commit()

        user = User.query.get(new_user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email,"testuser@gmail.com")
        self.assertTrue(user.password.startswith('$2b$'))

    def test_signup_fail(self):
        """ test user wrong input """

        wrong_username = User.signup(None,"testuser@gmail.com","password",None)
        with self.assertRaises(exc.IntegrityError) as context: 
            db.session.commit()
        db.session.rollback()

        wrong_email = User.signup("testuser",None,"password",None)
        with self.assertRaises(exc.IntegrityError) as context: 
            db.session.commit()

        with self.assertRaises(ValueError) as context: 
            wrong_password = User.signup("testuser","testuser@gmail.com", None,None)


    def test_authenticate(self):
        """ test authentication method """

        user = User.authenticate(self.u1.username, 'pass')
        self.assertIsNotNone(user)
        self.assertEqual(user.id,self.u1.id)

        wrong_username = User.authenticate('wrongname', 'pass')
        self.assertFalse(wrong_username)

        wrong_password = User.authenticate(self.u1.username, 'wrongpass')
        self.assertFalse(wrong_password)