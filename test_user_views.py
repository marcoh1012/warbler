""" User View Tests """
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """ Test Views for User """

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser_id=1111
        self.testuser.id=self.testuser_id

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        self.testuser2_id=2222
        self.testuser2.id=self.testuser2_id


        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_users_all(self):
        """ Test list users route"""

        with self.client as c:
            resp = c.get('/users')

            self.assertIn('testuser', str(resp.data))
            self.assertIn('testuser2', str(resp.data))

            resp = c.get('/users?q=testuser2')
            self.assertIn('testuser2', str(resp.data))

    def test_users_show(self):
        """ Test users show route """

        with self.client as c:
            resp=c.get('/users/1111')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', str(resp.data))
            self.assertNotIn('testuseer2', str(resp.data))


    def test_show_following(self):
        """ Test show following """

        follows = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser.id)
        db.session.add(follows)
        db.session.commit()
        
        with self.client as c:
            resp = c.get('/users/2222/following', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('/users/1111/following', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser2', str(resp.data))

    def test_user_followers(self):
        """ Test user followers """

        follows = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser.id)
        db.session.add(follows)
        db.session.commit()
        
        with self.client as c:
            resp = c.get('/users/1111/followers', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id

            resp = c.get('/users/1111/followers', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', str(resp.data))

    def test_add_follow(self):
        """ Test add follow """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post('/users/follow/2222', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser2', str(resp.data))

    def test_stop_follow(self):
        """ Test stop follow """

        follows = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser.id)
        db.session.add(follows)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post('/users/stop-following/2222', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('testuser2', str(resp.data))

    def test_profile(self):
        """ test profile """

        with self.client as c:
            resp = c.get('/users/profile', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('/users/profile', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', str(resp.data))
            self.assertIn('test@test.com', str(resp.data))
            self.assertIn('Bio', str(resp.data))
            self.assertIn('password', str(resp.data))

    