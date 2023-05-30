from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length


class ExerciseForm(FlaskForm):
    """Form for adding/editing exercises."""

    name = StringField('Exercise Name', validators=[DataRequired()])
    type = SelectMultipleField('Exercise Type', choices=[("cardio", "Cardio"), ("olympic_weightlifting", "Olympic Weight Lifting"), ("plyometrics", "Plyometrics"), (
        "powerlifting", "Powerlifting"), ("strength", "Strength"), ("stretching", "Stretching"), ("strongman", "Strongman")], validators=[DataRequired()])
    muscle = SelectMultipleField('Muscle Group', choices=[("abdominals", "Abdominals"), ("abductors", "Abductadductors", "Adductors"), ("biceps", "Biceps"), ("calves", "Calves"), ("chest", "Chest"), ("forearms", "Forearms"), ("glutes", "Glutes"), (
        "hamstrings", "Hamstrings"), ("lats", "Lats"), ("lower_back", "Lower Back"), ("middle_back", "Middle Back"), ("neck", "Neck"), ("quadriceps", "Quads"), ("traps", "Traps"), ("triceps", "Triceps")], validators=[DataRequired()])
    equipment = StringField('Equipment Required', validators=[DataRequired()])
    difficulty = SelectMultipleField('Difficulty', choices=[("beginner", "Beginner"), (
        "intermediate", "Intermediate"), ("expert", "Expert")], validators=[DataRequired()])
    instructions = StringField('Instructions', validators=[DataRequired()])


class MemberAddForm(FlaskForm):
    """Form for adding members"""

    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    image_url = StringField('Image URL', validators=[DataRequired()])
    bio = StringField('(Optional) Bio')
    location = StringField('(Optional) Location')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class MemberEditForm(FlaskForm):
    """Form for editing member information"""
    username = StringField('Username')
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    bio = TextAreaField('(Optional) Tell us about yourself')
    password = PasswordField("Password", validators=[Length(min=6)])
