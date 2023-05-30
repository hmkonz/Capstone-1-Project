"""SQLAlchemy models for Capstone One Project"""
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
bcrypt = Bcrypt()
db = SQLAlchemy()


class Member(db.Model):
    """Member in the system."""
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text, nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)

    workouts = db.relationship('Workout', backref='members')

    def __repr__(self):
        return f"<Member #{self.id}: {self.username}, {self.first_name}, {self.last_name}, {self.email}>"

    @classmethod
    def signup(cls, username, first_name, last_name, email, password, image_url, bio, location):
        """Sign up member. Hashes password and adds member to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        member = Member(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            bio=bio,
            location=location)

        db.session.add(member)
        db.session.commit()
        return member

    @classmethod
    def authenticate(cls, username, password):
        """Find member with `username` and `password`.
        This is a class method (call it on the class, not on an individual member.)
        It searches for a member whose password hash matches this password
        and, if it finds such a member, returns that member object.
        If can't find matching member (or if password is wrong), returns False."""

        member = cls.query.filter_by(username=username).first()

        if member:
            is_auth = bcrypt.check_password_hash(member.password, password)
            if is_auth:
                return member
        return False


class Workout(db.Model):
    """An individual workout"""

    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))

    workout_date = db.Column(db.Date, nullable=False,
                             default=datetime.now().strftime("%A %b %d %Y"))

    exercises = db.relationship(
        "Exercise", secondary="workout_exercises", backref="workouts", cascade='all,delete')


class WorkoutExercise(db.Model):
    """Mapping workout to exercises"""

    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey(
        'workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey(
        'exercises.id'), nullable=False)
    workout_date = db.Column(db.Date, nullable=False,
                             default=datetime.now().strftime("%A %b %d %Y"))


class Exercise(db.Model):
    """An individual exercise"""

    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    type = db.Column(db.Text, nullable=False)
    muscle = db.Column(db.Text, nullable=False)
    equipment = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)


def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app. """
    db.app = app
    db.init_app(app)
