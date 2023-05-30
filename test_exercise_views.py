"""Member View tests."""
# run these tests like:   FLASK_ENV=production python -m unittest test_exercise_views.py

from app import app, CURR_MEMBER_KEY
import os
from app import app
from unittest import TestCase
import requests
from datetime import datetime
from flask import session

from models import db, connect_db, Member, Exercise, Workout


# BEFORE we import our app, let's set an environmental variable to use a different database for tests (we need to do this before we import our app, since that will have already connected to the database)
os.environ['DATABASE_URL'] = "postgresql:///exercises_test"

# Now we can import app

# Don't clutter tests with SQL
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
# Don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables once for all tests --- in each test, we'll delete the data  and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class ExerciseViewsTestCase(TestCase):
    """Tests for views of Exercise API."""

    def setUp(self):
        """Make demo data."""

        db.drop_all()
        db.create_all()

        self.testmember = Member.signup(
            username="testuser",
            first_name="testfirstname",
            last_name="testlastname",
            email="test@test.com",
            image_url="default_profile_pic.jpg",
            bio="testbio",
            location="testlocation",
            password="password",
        )

        self.testmember.id = 8989

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_show_homepage_logged_in(self):
        with app.test_client() as client:

            with client.session_transaction() as change_session:
                change_session[CURR_MEMBER_KEY] = self.testmember.id

            response = client.get('/')
            # if member is logged in, redirects to "/exercises" page (redirect has a status code of 302)
            self.assertEqual(response.status_code, 302)

    def test_show_homepage_logged_out(self):
        with app.test_client() as client:

            response = client.get('/')
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(
                '<h1 class="homepage-title">Ready to Workout?</h1>', html)

    def test_show_member_noWorkout(self):
        with app.test_client() as client:

            with client.session_transaction() as change_session:
                change_session[CURR_MEMBER_KEY] = self.testmember.id

            response = client.get(f"/members/{self.testmember.id}")

            # if member hasn't created any workouts, redirects to "/exercises" page (redirect has a status code of 302)
            self.assertEqual(response.status_code, 302)

    def test_show_member_hasWorkout(self):

        workout = Workout(id=1, member_id=self.testmember.id,
                          workout_date="2023-05-24")

        db.session.add(workout)
        db.session.commit()

        self.assertIsNotNone(workout)

        with app.test_client() as client:

            with client.session_transaction() as change_session:
                change_session[CURR_MEMBER_KEY] = self.testmember.id

            response = client.get(f"/members/{self.testmember.id}")

            self.assertEqual(response.status_code, 200)
            self.assertIn(
                'testfirstname testlastname', str(response.data))

    def test_show_exercises_logged_in(self):
        with app.test_client() as client:

            with client.session_transaction() as change_session:
                change_session[CURR_MEMBER_KEY] = self.testmember.id

            response = client.get("/exercises")

            self.assertEqual(response.status_code, 200)
            self.assertIn(
                'Cardio', str(response.data))

    def test_show_exercises_logged_out(self):
        with app.test_client() as client:

            response = client.get("/exercises")
            # if member is not logged in, redirects to "/login" page (redirect has a status code of 302)
            self.assertEqual(response.status_code, 302)

    def test_show_cardio_exercises_logged_in(self):
        with app.test_client() as client:

            with client.session_transaction() as change_session:
                change_session[CURR_MEMBER_KEY] = self.testmember.id

            response = client.get("/exercises/cardio")

            self.assertEqual(response.status_code, 200)
            self.assertIn(
                'Jumping rope', str(response.data))

    def test_show_cardio_exercises_logged_out(self):
        with app.test_client() as client:

            response = client.get("/exercises/cardio")
            # if member is not logged in, redirects to "/" page (redirect has a status code of 302)
            self.assertEqual(response.status_code, 302)
