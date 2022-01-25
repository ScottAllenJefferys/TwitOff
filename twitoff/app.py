from flask import Flask, render_template
from .models import DB, User, Tweet
# The DOT says that the file is in the same folder
# Its just to avoid having to write out the entire path

# 'Factory' function to create the app


def create_app():

    app = Flask(__name__)

    # Configuration variable for our app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Connecto ur DB to the app object
    DB.init_app(app)

    @app.route("/")
    def home_page():
        # initialize on first run
        # Checks IF EXISTS by default to prevent recreating tables
        DB.create_all()
        # query for all users in the database
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

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
        # Reset tables first
        # Drop old DB Tables
        DB.drop_all()
        # Make new DB Tables
        DB.create_all()

        # Make two new users
        ryan = User(id=1, username='ryanallred')
        julian = User(id=2, username='julian')

        # Make two tweets and attach the tweets to those users
        tweet1 = Tweet(id=1, text="this is ryan's tweet", user=ryan)
        tweet2 = Tweet(id=2, text="this is julian's tweet", user=julian)

        # Insert them into the table
        DB.session.add(ryan)
        DB.session.add(julian)
        DB.session.add(tweet1)
        DB.session.add(tweet2)

        # Just like SQLite needs .commit()
        DB.session.commit()

        users = User.query.all()
        return render_template('base.html', title='Populate Database', users=users)

    return app
