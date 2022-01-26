from flask import Flask, render_template, request
from .models import DB, User, Tweet
# The DOT says that the file is in the same folder
# Its just to avoid having to write out the entire path
from os import getenv
from .twitter import add_or_update_user

# 'Factory' function to create the app


def create_app():

    app = Flask(__name__)

    # Configuration variable for our app
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Connect the DB to the app object
    DB.init_app(app)

    @app.route("/", methods=['GET', 'POST'])
    def home_page():
        # initialize the Databse on first run
        # Checks IF EXISTS by default to prevent recreating tables
        DB.create_all()

        # THIS SOMEHOW ALLOWS HTML FORM INPUT
        if request.method == "POST":
            add_or_update_user(request.form.get("new_username"))

        # query for all users in the database
        users = User.query.all()

        return render_template('home.html', title='Home', users=users)

    @app.route('/reset')
    def reset():
        # We want to do some database stuff inside here
        # Drop old DB Tables
        DB.drop_all()
        # Make new DB Tables
        DB.create_all()
        return render_template('base.html', title='Reset Database')

    @app.route('/populate')
    # Test database functionality
    # by inserting some fake data into the DB
    def populate():

        add_or_update_user('nasa')

        add_or_update_user('nntaleb')

        users = User.query.all()
        return render_template('base.html', title='Populate Database', users=users)

    @app.route('/update')
    def update():

        usernames = get_usernames()
        for username in usernames:
            add_or_update_user(username)

        users = User.query.all()
        return render_template('home.html', title='Update User Tweets', users=users)

    return app


def get_usernames():
    # get all of the usernames of existing users
    Users = User.query.all()
    usernames = []
    for user in Users:
        usernames.append(user.username)
    return usernames
