"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
    
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        self.testmsg = Message(text="Hi, this is test message!", user_id=self.testuser.id)

        db.session.add(self.testmsg)
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.order_by(Message.id.desc()).first()
            self.assertEqual(msg.text, "Hello")

    def test_unauthorized_add_message(self):
        """User can't send message without authprized"""

        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("Log in", html)

    def test_message_show(self):
        """Message can be viewed"""

        with self.client as c:

            resp = c.get(f"/messages/{self.testmsg.id}")
            html = resp.get_data(as_text=True)
     
            self.assertEqual(resp.status_code, 200)
    

    def test_message_delete(self):
        """Message can delete from current user"""  

        u = User.signup(username="user",
                        email="testtest@test.com",
                        password="password12",
                        image_url=None)
        u.id = 1111

   
        m = Message(
            id=2222,
            text="message",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1111

            resp = c.post("/messages/2222/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            msg = Message.query.get(2222)
            self.assertIsNone(msg)



