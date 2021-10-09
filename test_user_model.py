"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

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




class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("testuser1", "testuser@gmail.com", "testUser12", None)
        id1 = 3333
        u1.id = id1

        image_url = "https://cdn.pixabay.com/photo/2014/11/30/14/11/cat-551554__340.jpg"
        u2 = User.signup("testuser2", "testuser2@gmail.com", "tesUSer45", image_url) 
        id2 = 4444
        u2.id = id2

        db.session.commit()

        self.user1 = User.query.get(id1)
        self.user2 = User.query.get(id2)

        self.u1id = id1
        self.u2id = id2
        

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

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

    # 
    # Sign Up Tests 
    #
    def test_user_valid_signup(self):
     
        self.assertEqual(self.user1.username, "testuser1")
        self.assertEqual(self.user1.email, "testuser@gmail.com", )
        self.assertEqual(self.user1.image_url, "/static/images/default-pic.png")

    def test_invalid_usernname_signup(self):

        invalid_user = User.signup("testuser1", "test@gmail.com", "test123", None)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_invalid_email_signup(self):

        invalid_user = User.signup("test", "testuser@gmail.com", "test", None)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_invalid_password_signup(self):

        with self.assertRaises(ValueError):
            invalid_user = User.signup("testtest", "user@email.com", "", None)

        with self.assertRaises(ValueError):
            invalid_user = User.signup("testtest", "user@email.com", None, None)


    # 
    # Sign In Tests 
    #

    def test_valid_sign(self):

        login_user1 = User.authenticate("testuser1", "testUser12")
        login_user2 = User.authenticate("testuser2", "tesUSer45")

        self.assertEqual(self.user1, login_user1)
        self.assertEqual(self.user2, login_user2)


    def test_invalid_sign(self):

        login_user1 = User.authenticate("testuser1", "testUser")
        login_user2 = User.authenticate("testuse", "tesUSer45")

        self.assertFalse(login_user1)
        self.assertFalse(login_user2)


    # 
    # User Following and Followers Tests 
    #

    def test_user_following(self):

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(self.user1.following[0], self.user2)
        self.assertTrue(self.user1.is_following(self.user2))


    def test_user_followers(self):

        self.user1.followers.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.followers), 1)
        self.assertEqual(self.user1.followers[0], self.user2)
        self.assertTrue(self.user1.is_followed_by(self.user2))
















