from flask import Flask, render_template, request, redirect, session, flash, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, Member, WorkoutExercise, Exercise, Workout
from forms import ExerciseForm, MemberAddForm, LoginForm, MemberEditForm
import requests
import json
import os
from datetime import datetime


CURR_MEMBER_KEY = "curr_member"
app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///exercise_db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get(
    "SQLALCHEMY_TRACK_MODIFICATIONS", False)
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO", True)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "abc123")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = os.environ.get(
    "DEBUG_TB_INTERCEPT_REDIRECTS", False)

toolbar = DebugToolbarExtension(app)

app.app_context().push()

connect_db(app)
db.create_all()


# ##############################################################################
# Member signup/login/logout

@app.before_request
def add_member_to_g():
    """If we're logged in, add curr member to Flask global 'g'"""

    if CURR_MEMBER_KEY in session:
        g.member = Member.query.get(session[CURR_MEMBER_KEY])

    else:
        g.member = None


def do_login(member):
    """Log in member"""

    session[CURR_MEMBER_KEY] = member.id


def do_logout():
    """Logout member"""

    if CURR_MEMBER_KEY in session:
        del session[CURR_MEMBER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle member signup"""

    # Create new member and add to DataBase. Redirect to home page.
    # If username is taken: flash message and re-present form.
    # Or if form not valid, present form.

    if CURR_MEMBER_KEY in session:
        del session[CURR_MEMBER_KEY]

    form = MemberAddForm()

    # execute the following if request is a POST request AND token is valid (gets values that member entered in MemberAddform); otherwise, return signup form again
    if form.validate_on_submit():
        # use ‘signup’ class method on instance of Member (member) to register a new member with info from MemberAddForm by adding 'member' to the database
        try:
            member = Member.signup(
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                image_url=form.image_url.data or Member.image_url.default.arg,
                password=form.password.data,
                bio=form.bio.data,
                location=form.location.data
            )
            db.session.commit()

        # if username is already taken, flash this warning and return to signup form
        except IntegrityError as e:
            db.session.rollback()
            flash("Username already taken. Please sign in again.", 'danger')
            return render_template("signup.html", form=form)

        # logs in the member after signup form is filled in
        do_login(member)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Produce login form or handle member login."""

    form = LoginForm()
    # execute the following if request is a POST request AND token is valid (gets values member entered in Loginform);
    if form.validate_on_submit():
        member = Member.authenticate(form.username.data, form.password.data)

        if member:
            do_login(member)
            flash(f"Hello, {member.first_name}!", "success")
            return redirect("/")

        else:
            flash("Invalid credentials. Please login again.", 'danger')

    """If criteria cannot be met, show login form"""
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of member"""
    do_logout()
    return redirect("/")


#################################################################################
# Home Page

@app.route('/')
def homepage():
    """Show choices of exercises if logged in; otherwise show home page"""
    if g.member:
        return redirect('/exercises')
    else:
        return render_template("home.html")


###################################################################################
# Member pages

@app.route('/members/<int:member_id>')
def show_member(member_id):
    """Show a page with info on a specific member and their log of workouts"""

    # retrieve member info from database based on their member_id
    member = Member.query.get_or_404(member_id)

    # retrieve workouts from database in descending order of date created; member.workouts won't be in order by default
    workouts = (Workout
                .query
                .filter(Workout.member_id == member_id)
                .order_by(Workout.workout_date.desc())
                .all())
    # if member has workouts created:
    if workouts:
        return render_template('member_profile.html', member=member, workouts=workouts)

    # if no workouts are in the member profile:
    else:
        flash("There are no workouts in your account. Select the exercises you want to add to today's workout!", "danger")
        return redirect('/exercises')


@app.route('/members/<int:member_id>/edit', methods=["GET", "POST"])
def edit_profile(member_id):
    """Handle form submission for updating an existing member if request is a POST request AND token is valid (gets values member entered in Loginform);"""

    if not g.member:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # retrieves input from form for the member that's logged in
    form = MemberEditForm(obj=g.member)
    # checks to see if request is a POST request AND if token is valid
    if form.validate_on_submit():
        # authenticate() checks to see if username and password input in form are those of the logged in member:
        if Member.authenticate(g.member.username, form.password.data):
            g.member.username = form.username.data
            g.member.email = form.email.data
            g.member.image_url = form.image_url.data or "/static/images/default-pic.png"
            g.member.bio = form.bio.data

            db.session.commit()

            flash("Profile Updated!", 'success')
            return redirect(f"/members/{g.member.id}")

        # if password input in form is incorrect:
        flash("Wrong password, please try again.", 'danger')
    # execute if a GET request OR token isn't valid
    return render_template('member_edit.html', form=form, member_id=g.member.id)


@app.route('/members/delete', methods=["POST"])
def delete_member():
    """Delete member"""

    if not g.member:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    # call function to delete member from database
    do_logout()

    db.session.delete(g.member)
    db.session.commit()

    return redirect("/signup")


###################################################################################
# Exercise pages

@app.route('/exercises')
def show_exercise_choices():
    """Show choices of exercises page if member is logged in; otherwise, redirect to login page"""

    if g.member:
        return render_template('exercise_choices.html')
    else:
        return redirect("/login")


@app.route('/exercises/cardio')
def show_cardio_exercises():
    """ Show a list of cardio exercises to choose from if member is logged in; otherwise, flash error messange and redirect to homepage"""

    non_duplicate_results = []
    type = 'cardio'
    name = 'Cardio'

    api_url = 'https://api.api-ninjas.com/v1/exercises?type={}'.format(type)

    response = requests.get(
        api_url, headers={'X-Api-Key': '9NXRdadudV9r0D3QNO516BKZ8VeFXZD3Nq15zrRv'})

    if g.member and response.status_code == requests.codes.ok:

        results = response.json()

        # removes any duplicated exercises from API response by only adding unique exercises to non_duplicated_results list
        for result in results:
            if result not in non_duplicate_results:
                non_duplicate_results.append(result)

        return render_template('exercise_categories.html', results=non_duplicate_results, type=type, name=name)

        """If criteria cannot be met, redirect to home page"""
    else:
        flash("Ooops something went wrong. Please try again", 'danger')
        return redirect('/')


@app.route('/exercises/olympic_weightlifting')
def show_olympic_weightlifting_exercises():
    """Show a list of olympic weightlifting exercises to choose from """

    non_duplicate_results = []
    type = 'olympic_weightlifting'
    name = 'Olympic Weightlifting'

    api_url = 'https://api.api-ninjas.com/v1/exercises?type={}'.format(type)

    response = requests.get(
        api_url, headers={'X-Api-Key': '9NXRdadudV9r0D3QNO516BKZ8VeFXZD3Nq15zrRv'})

    if g.member and response.status_code == requests.codes.ok:

        results = response.json()

        # removes any duplicated exercises from API response by only adding unique exercises to non_duplicated_results list
        for result in results:
            if result not in non_duplicate_results:
                non_duplicate_results.append(result)

        return render_template('exercise_categories.html', results=non_duplicate_results, type=type, name=name)

        """If criteria cannot be met, redirect to home page"""
    else:
        flash("Ooops something went wrong. Please try again", 'danger')
        return redirect('/')


@app.route('/exercises/plyometrics')
def show_plyometric_exercises():
    """Show a list of plyometric exercises to choose from """

    non_duplicate_results = []
    type = 'plyometrics'
    name = 'Plyometric'

    api_url = 'https://api.api-ninjas.com/v1/exercises?type={}'.format(type)

    response = requests.get(
        api_url, headers={'X-Api-Key': '9NXRdadudV9r0D3QNO516BKZ8VeFXZD3Nq15zrRv'})

    if g.member and response.status_code == requests.codes.ok:

        results = response.json()

        # removes any duplicated exercises from API response by only adding unique exercises to non_duplicated_results list
        for result in results:
            if result not in non_duplicate_results:
                non_duplicate_results.append(result)

        return render_template('exercise_categories.html', results=non_duplicate_results, type=type, name=name)

        """If criteria cannot be met, redirect to home page"""
    else:
        flash("Ooops something went wrong. Please try again", 'danger')
        return redirect('/')


@app.route('/exercises/powerlifting')
def show_powerlifting_exercises():
    """Show a list of powerlifting exercises to choose from """

    non_duplicate_results = []
    type = 'powerlifting'
    name = 'Powerlifting'

    api_url = 'https://api.api-ninjas.com/v1/exercises?type={}'.format(type)

    response = requests.get(
        api_url, headers={'X-Api-Key': '9NXRdadudV9r0D3QNO516BKZ8VeFXZD3Nq15zrRv'})

    if g.member and response.status_code == requests.codes.ok:

        results = response.json()

        # removes any duplicated exercises from API response by only adding unique exercises to non_duplicated_results list
        for result in results:
            if result not in non_duplicate_results:
                non_duplicate_results.append(result)

        return render_template('exercise_categories.html', results=non_duplicate_results, type=type, name=name)

        """If criteria cannot be met, redirect to home page"""
    else:
        flash("Ooops something went wrong. Please try again", 'danger')
        return redirect('/')


@app.route('/exercises/strength')
def show_strength_exercises():
    """Show a list of strength exercises to choose from """

    non_duplicate_results = []
    type = 'strength'
    name = 'Strength'

    api_url = 'https://api.api-ninjas.com/v1/exercises?type={}'.format(type)

    response = requests.get(
        api_url, headers={'X-Api-Key': '9NXRdadudV9r0D3QNO516BKZ8VeFXZD3Nq15zrRv'})

    if g.member and response.status_code == requests.codes.ok:

        results = response.json()

        # removes any duplicated exercises from API response by only adding unique exercises to non_duplicated_results list
        for result in results:
            if result not in non_duplicate_results:
                non_duplicate_results.append(result)

        return render_template('exercise_categories.html', results=non_duplicate_results, type=type, name=name)

        """If criteria cannot be met, redirect to home page"""
    else:
        flash("Ooops something went wrong. Please try again", 'danger')
        return redirect('/')


@app.route('/exercises/stretching')
def show_stretching_exercises():
    """Show a list of stretching exercises to choose from """

    non_duplicate_results = []
    type = 'stretching'
    name = 'Stretching'

    api_url = 'https://api.api-ninjas.com/v1/exercises?type={}'.format(type)

    response = requests.get(
        api_url, headers={'X-Api-Key': '9NXRdadudV9r0D3QNO516BKZ8VeFXZD3Nq15zrRv'})

    if g.member and response.status_code == requests.codes.ok:

        results = response.json()

        # removes any duplicated exercises from API response by only adding unique exercises to non_duplicated_results list
        for result in results:
            if result not in non_duplicate_results:
                non_duplicate_results.append(result)

        return render_template('exercise_categories.html', results=non_duplicate_results, type=type, name=name)

        """If criteria cannot be met, redirect to home page"""
    else:
        flash("Ooops something went wrong. Please try again", 'danger')
        return redirect('/')


@app.route('/exercises/strongman')
def show_strongman_exercises():
    """Show a list of strongman exercises to choose from """

    non_duplicate_results = []
    type = 'strongman'
    name = 'Strongman'

    api_url = 'https://api.api-ninjas.com/v1/exercises?type={}'.format(type)

    response = requests.get(
        api_url, headers={'X-Api-Key': '9NXRdadudV9r0D3QNO516BKZ8VeFXZD3Nq15zrRv'})

    if g.member and response.status_code == requests.codes.ok:

        results = response.json()

        # removes any duplicated exercises from API response by only adding unique exercises to non_duplicated_results list
        for result in results:
            if result not in non_duplicate_results:
                non_duplicate_results.append(result)

        return render_template('exercise_categories.html', results=non_duplicate_results, type=type, name=name)

        """If criteria cannot be met, redirect to home page"""
    else:
        flash("Ooops something went wrong. Please try again", 'danger')
        return redirect('/')


@app.route('/exercises/<path:exercise>')
def exercise_description(exercise):
    """Show details and options about a specific exercise """
    args = request.args
    type = args.get('type')
    workout_id = args.get('workout_id')
    name = f"{exercise}"
    member = g.member

    api_url = 'https://api.api-ninjas.com/v1/exercises?name={}'.format(name)

    response = requests.get(
        api_url, headers={'X-Api-Key': '9NXRdadudV9r0D3QNO516BKZ8VeFXZD3Nq15zrRv'})

    results = []

    if not g.member:
        flash("Ooops something went wrong. Please try again", 'danger')
        return redirect('/')

    elif response.status_code == requests.codes.ok:

        for resp in response.json():
            # retrieve first exercise in database with specific name
            exercise = Exercise.query.filter_by(name=resp.get('name')).first()
            # shows the details of an exercise
            if type == None:
                return render_template('exercise_detail2.html', name=name, member_id=member.id, workout_id=workout_id, exercise=exercise, response=response.json())

            # adds a new exercise from the API to the database and the 'results' list if it's not already in there
            elif exercise == None or resp.get('name') != exercise.name:

                new_exercise = Exercise(name=resp.get('name'), type=resp.get('type'), muscle=resp.get('muscle'), equipment=resp.get(
                    'equipment'), difficulty=resp.get('difficulty'), instructions=resp.get('instructions'))

                db.session.add(new_exercise)
                results.append(new_exercise)

            else:
                # if the exercise retrieved from the database with a spefic name is not in the results list, add it
                if exercise not in results:
                    results.append(exercise)

        db.session.commit()

    return render_template('exercise_detail1.html', type=type, results=results, name=name, member=member)


###################################################################################
# Workout pages


@app.route('/members/<int:member_id>/workout_page', methods=["GET", "POST"])
def add_exercises_to_workout(member_id):
    """Retrieve a list of the exercises selected with checked boxes by a member and add them to the member's workout page"""

    if not g.member:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    type = request.form.get('type')
    dt = datetime.now()
    today_date = dt.strftime("%A %b %d %Y")

    # retrieve the exercises selected with checked boxes
    selected_exercises = request.form.getlist('type-of-exercise')

    # retrieve a specific workout based on the date it was created and the member_id
    workout = Workout.query.filter_by(
        workout_date=today_date, member_id=g.member.id).first()

    # if there isn't a workout fitting the above criteria in the database, create that workout and add it to the database
    if not workout:

        workout = Workout(member_id=g.member.id, workout_date=today_date)
        db.session.add(workout)

    # loop through the list of 'selected_exercises':
    for exercise_name in selected_exercises:
        # retrieve all the exercises in the database with the name of the iterated exercise ('exercise_name') in the 'selected_exercise's list
        existing_exercises = Exercise.query.filter_by(name=exercise_name).all()
        # if an exercise exists in the database (in existing_exercies), add it to the exercises of the specific workout retrieved above
        for exercise in existing_exercises:
            workout.exercises.append(exercise)

    db.session.commit()

    return render_template('member_workout_page.html', type=type, date=today_date, workout=workout, member_id=member_id)


@app.route("/members/<int:member_id>/workouts/<int:workout_id>", methods=["GET"])
def show_member_workout(member_id, workout_id):
    """Show details of a member's specific workout including the date created and all the exercises included in that workout"""

    member_id = g.member.id

    # retrieve data about a specific workout based on its id
    workout = Workout.query.get_or_404(workout_id)

    return render_template('workout_detail.html', workout=workout, member_id=member_id, workout_id=workout_id)
