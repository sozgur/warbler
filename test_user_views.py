"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

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


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
    
        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser1.id = 1111

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser2.id = 2222

        self.testuser3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser3.id = 3333

        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_list(self):
        """User list"""

        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("@testuser3", str(resp.data))

    def test_user_search(self):
        """User search with username"""

        with self.client as c:

            resp = c.get("/users?q=testuser1")

            self.assertIn("@testuser1", str(resp.data))
            self.assertNotIn("@testuser2", str(resp.data))
            self.assertNotIn("@testuser3", str(resp.data))

    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/1111")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", str(resp.data))

    def setup_likes(self):
        m1 = Message(id=1234, text="Hello", user_id=1111)
        m2 = Message(id=3456, text="Hi", user_id=1111)
        m3 = Message(id=9876, text="Goodbye", user_id=2222)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        self.testuser3.likes.extend([m1, m2, m3])
        db.session.commit()

    def test_user_show(self):
        self.setup_likes()

        with self.client as c:

            resp = c.get("/users/3333")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser3", str(resp.data))
            self.assertEqual(len(self.testuser3.likes), 3)

            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find(id="like-count")
           
            self.assertEqual(found.text, "3")


    def test_toggle_like(self):
        m = Message(id=1234, text="Message", user_id=self.testuser1.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.post("/users/toggle_like/1234", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==1234).all()
            self.assertEqual(len(likes), 1)

            resp = c.post("/users/toggle_like/1234", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==1234).all()
            self.assertEqual(len(likes), 0)


    def test_unauthenticated_like(self):
        m = Message(id=1234, text="Message", user_id=self.testuser1.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.post(f"/users/toggle_like/{m.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))


    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.testuser1.id, user_following_id=self.testuser2.id)
        f2 = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser1.id)
        f3 = Follows(user_being_followed_id=self.testuser1.id, user_following_id=self.testuser3.id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_user_show_with_follows(self):

        self.setup_followers()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser1.id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser1", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            following = soup.find(id="following-count")
            followers = soup.find(id="followers-count")
           
            self.assertEqual(following.text, "1")
            self.assertEqual(followers.text, "2")



    