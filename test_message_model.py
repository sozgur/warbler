"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Likes
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




class MessageModelTestCase(TestCase):
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

    def test_message_model(self):
        """Does basic model work?"""

        msg = Message(
            text="Test Message",
            user_id=self.u1id
        )

        db.session.add(msg)
        db.session.commit()

        # Message belongs to the user1
        self.assertEqual(msg.user, self.user1)

    def test_message_like(self):

        msg1 = Message(
            text="Hello, This is message from user1",
            user_id=self.u1id
        )

        msg2 = Message(
            text="Good morning!",
            user_id=self.u2id
        )

        db.session.add_all([msg1, msg2])
        db.session.commit()

        self.user1.likes.extend([msg1, msg2])
        db.session.commit()

        self.assertEqual(len(self.user1.likes), 2)
        self.assertEqual(len(self.user2.likes), 0)
        self.assertEqual(self.user1.likes[0], msg1)













