# LET'S WORKOUT!

Deployed on Render.com: https://letsworkouttoday.onrender.com

## About

"Let's Workout" is a website that allows a logged-in member to peruse through thousands of exercises and choose which ones they want to add to their day's workout.  This app allows a member to create and edit their account, choose exercises to add to their workouts based on specific criteria and save them to their day's workout. A log of all created workouts is displayed on the member's profile page so members can go back and look at any of their previous workout details. 

### Website Features
#### Search Exercises
Members submit search requests for different types of exercises, and data from these searches are sent as a request to one of the various API Ninjas Exercises endpoints to receive relevant exercises options to select from. Search options include name of exercise, type of exercise, muscles used, difficulty level, instructions and equipment needed.

#### Exercise Categories Page
When navigating to the exercise page, members are shown images of 7 different types of exercise categories they can click on to retrieve the exercise options in that category. These options are acquired from the "type" endpoint of the API Ninjas exercises Web API (i.e. cardio). 

#### Exercise Details/Options Page
Any exercise a member clicks on within a category (i.e. jumping rope in the cardio category) will be the new endpoint in another API request that retrieves all the exercises pertaining to that exercise option (i.e. different types of jump roping exercises). If desired, the member can select any of these exercise options and add them to their day's workout and/or go back and search for another type of exercise either within the same category or in a different category to add to their workout. The exercises selected are then displayed on the member's workout page.

#### Member Workout Page
When a member selects exercises from the exercise details/options page that they want to do that day, those exercises are added to "Today's Workout" page. Each of those exercises are then able to be clicked on so if the member wants to see the exercise details again before they perform them, they can. Details shown are muscle group worked, equipment required, difficulty level and instructions.

#### Specific Workout Page
Each workout in the log displayed on the member's profile page can be clicked on for more details. The date the workout was created as well as the exercises included in that workout are displayed. If the member wants to see the exercise details of the workout, each exercise can be clicked on to display the muscle group worked, equipment required, difficulty level and instructions. 

#### Member Profile Page
The member profile page displays the member's picture, bio and location, if the member added them when they signed up. Additionally, a log of every workout is displayed in descending order of date created. 

### Sign Up/Log in:
Members sign up with username, first name, last name, email, password, image (optional), bio (optional) and location (optional). Password is hashed using Bcrypt. Only logged in members are able to request exercises from the API, add them to their day's workout, see a log of workouts created on their profile page as well as the exercises included in each workout created.

### Tech Stack

HTML, CSS, Jinja, Python, Flask, PostgreSQL, SQLAlchemy, Bcrypt, WTForms, Jinja
