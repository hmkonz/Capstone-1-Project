# """Member model tests."""

# run these tests like:  python -m unittest test_member_model.py
from app import app
import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, Exercise, Member

# BEFORE we import our app, let's set an environmental variable  to use a different database for tests (we need to do this before we import our app, since that will have already connected to the database)
os.environ['DATABASE_URL'] = "postgresql:///exercises_test"

# Now we can import app

# Don't clutter tests with SQL
app.config['SQLALCHEMY_ECHO'] = False


# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
# Don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


db.drop_all()
db.create_all()


class MemberModelTestCase(TestCase):
    """Test views for workouts."""

    def setUp(self):
        """Create test client, add sample data."""
        # Delete the data and create fresh new clean test data before every test method in this class
        db.drop_all()
        db.create_all()

        # Add sample members
        member1 = Member.signup(
            "test1", "test1_firstname", "test1_lastname", "email1@email.com", "test1image", "test1bio", "test1location", "password")
        member1.id = 1111

        member2 = Member.signup(
            "test2", "test2_firstname", "test2_lastname", "email2@email.com", "test2image", "test2bio", "test2location", "password")
        member2.id = 2222

        db.session.commit()
        m1 = Member.query.get(member1.id)
        m2 = Member.query.get(member2.id)

        self.member1 = member1
        self.member1.id = member1.id
        self.member2 = member2
        self.member2.id = member2.id

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_member_model(self):
        """Does basic Member model work?"""

        member = Member(
            username="testmember",
            first_name="testfirstname",
            last_name="testlastname",
            email="test@test.com",
            image_url="testimage_url1",
            password="HASHED_PASSWORD"
        )

        db.session.add(member)
        db.session.commit()

        # Member should have no workouts
        self.assertEqual(len(member.workouts), 0)

    #####################################################################
    # Signup Tests
    ####################################################################

    def test_valid_signup(self):
        member_test = Member.signup("membertest", "memberfirstname", "memberlastname",
                                    "test@test.com", "password", "memberimage_url", "memberbio", "memberlocation")
        member_test.id = 99999
        db.session.commit()

        member_test = Member.query.get(member_test.id)
        self.assertIsNotNone(member_test)
        self.assertEqual(member_test.username, "membertest")
        self.assertEqual(member_test.email, "test@test.com")
        # password is encrypted when signup method is called so shouldn't equal "password"
        self.assertNotEqual(member_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(member_test.password.startswith("$2b$"))
        self.assertEqual(member_test.image_url, "memberimage_url")
        self.assertEqual(member_test.bio, "memberbio")
        self.assertEqual(member_test.location, "memberlocation")

    def test_invalid_username_signup(self):
        invalid = Member.signup(None, "memberfirstname", "memberlastname",
                                "test@test.com", "password", "memberimage_url", "memberbio", "memberlocation")
        invalid.id = 123456789
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = Member.signup("membertest", "memberfirstname", "memberlastname",
                                None, "password", "memberimage_url", "memberbio", "memberlocation")
        invalid.id = 123789
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            Member.signup("membertest", "memberfirstname", "memberlastname",
                          "test@test.com", "", "memberimage_url", "memberbio", "memberlocation")

        with self.assertRaises(ValueError) as context:
            Member.signup("membertest", "memberfirstname", "memberlastname",
                          "test@test.com", None, "memberimage_url", "memberbio", "memberlocation")


#####################################################################
    # Authentication Tests
    ####################################################################


    def test_valid_authentication(self):
        test_user = Member.signup("membertest", "memberfirstname", "memberlastname",
                                  "test@test.com", "password", "memberimage_url", "memberbio", "memberlocation")
        test_user.id = 99999
        db.session.commit()

        member1 = Member.authenticate(test_user.username, "password")

        self.assertIsNotNone(member1)
        self.assertEqual(member1.id, test_user.id)

    def test_invalid_username(self):
        self.assertFalse(Member.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(Member.authenticate(
            self.member1.username, "badpassword"))
