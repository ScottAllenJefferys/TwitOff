from flask import Flask, render_template, request
from .models import DB, User, Tweet
# The DOT says that the file is in the same folder
# Its just to avoid having to write out the entire path
from os import getenv
from .twitter import add_or_update_user
from .predict import predict_user

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
        # THIS SOMEHOW ALLOWS HTML FORM INPUT
        # if request.method == "POST":
        #     add_or_update_user(request.form.get("new_username"))

        return render_template('base.html', title='Home', users=User.query.all())

    @app.route('/reset')
    def reset():
        # We want to do some database stuff inside here
        # Drop old DB Tables
        DB.drop_all()
        # Make new DB Tables
        DB.create_all()
        return render_template('base.html', title='Database Has Been Reset')

    @app.route('/update')
    def update():

        usernames = get_usernames()

        for username in usernames:
            add_or_update_user(username)

        return render_template('base.html', title='All Users Updated', users=User.query.all())

    # normally we only allow GET requests, this restricts us to only POST (POST = changing database)
    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):
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
        user0, user1 = sorted([
            request.values['user0'], request.values['user1']
        ])

        if user0 == user1:
            message = 'Cannot compare a user to themselves'
        else:
            prediction = predict_user(
                user0, user1, request.values['tweet_text'])
            message = '"{}" is more likely to be said by {} than {}'.format(request.values['tweet_text'],
                                                                            user1 if prediction else user0,
                                                                            user0 if prediction else user1)

        return render_template('prediction.html', title="Prediction", message=message)

    return app


def get_usernames():
    # get all of the usernames of existing users
    Users = User.query.all()
    usernames = []
    for user in Users:
        usernames.append(user.username)
    return usernames
