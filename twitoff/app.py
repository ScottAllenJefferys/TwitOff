# ***********************************************************

# Web Application Framework: flask
from flask import Flask, render_template, request
# flask is based on the Werkzeg WSGI toolkit
#  and the Jinja2 template engine
# WSGI (web server gateway interface) is the
#  standard python interface between web servers
#  and web applications
# Jinja2 combines HTML templates with python
#  variables to render dynamic web pages

# Operating System Interaction: os
from os import getenv
# getenv(key) returns the value of the
#  environment variable key if it exists

# Database and Database Objects
from .models import DB, User, Tweet
# made with SQLAlchemy using SQLite3

# Twitter API Interaction
from .twitter import add_or_update_user
# add_or_update_user either adds a User
#  to the User table within the DB database
#  or adds any news Tweets to that User
#  if they were already in the database

# Machine Learning Functions
from .predict import predict_user

# ***********************************************************


def create_app():

    app = Flask(__name__)

    # Configuration variable for our app
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Connect the DB to the app object
    DB.init_app(app)

    @app.route("/", methods=['GET', 'POST'])
    def home_page():
        DB.create_all()

        return render_template('base.html', title='Home', users=User.query.all())

    @app.route('/reset')
    def reset():
        '''Resets the database'''
        # Drop old DB Tables
        DB.drop_all()
        # Make new DB Tables
        DB.create_all()
        return render_template('base.html', title='Database Has Been Reset')

    @app.route('/update')
    def update():
        '''Updates the tweets of all Users already in the database'''
        usernames = get_usernames()
        for username in usernames:
            add_or_update_user(username)
        return render_template('base.html', title='All Users Updated', users=User.query.all())

    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):
        '''Adds a new user to the database or fetches
           tweets for an existing user
        '''
        username = username or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'{username} successfully added'
            tweets = User.query.filter(
                User.username == username).one().tweets
        except Exception as e:
            message = f'Error adding {username}: {e}'

        return render_template('user.html', title=username, tweets=tweets, message=message)

    @app.route('/compare', methods=['POST'])
    def compare():
        '''Requests two usernames and a hypothetical tweet
           Returns prediction of which user is more likely
            to make that tweet
        '''
        user0, user1 = sorted([
            request.values['user0'], request.values['user1']
        ])
        # Prevent Self Comparison
        if user0 == user1:
            message = 'Cannot compare a user to themselves'
        else:
            prediction, probabilities = predict_user(
                user0, user1, request.values['tweet_text'])

            # Strength of Prediction
            times_more_likely = round(
                max(probabilities) / min(probabilities), 2) - 1

            # Message to be Displayed
            message = '"{}" is {} times more likely to be said by {} than {}'.format(request.values['tweet_text'],
                                                                                     times_more_likely,
                                                                                     user1 if prediction else user0,
                                                                                     user0 if prediction else user1)
        return render_template('prediction.html', title="Prediction", message=message)

    return app


def get_usernames():
    '''Get all of the usernames of existing users'''
    Users = User.query.all()
    usernames = []
    for user in Users:
        usernames.append(user.username)
    return usernames
