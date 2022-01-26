from flask_sqlalchemy import SQLAlchemy

# flask_sqlachemy lets us handle sql database management in python
# with functions that are independent of any SQL dialect

# Create a DB Object

DB = SQLAlchemy()  # Opens conneciton, makes cursor

# Create a table with a specific schema
# we will do that by creating a python class


class User(DB.Model):
    # Two columns inside of our user table

    # ID Column Schema
    # (similar to SQL strings but done through python functions)
    id = DB.Column(DB.BigInteger, primary_key=True, nullable=False)

    # Username Column Schema
    username = DB.Column(DB.String, nullable=False)

    # Tweets list is created by the .relationship and .backref in the Tweet class
    # tweets = []

    newest_tweet_id = DB.Column(DB.BigInteger)  # Used for updating tweet lists


class Tweet(DB.Model):

    # ID Column Schema
    id = DB.Column(DB.BigInteger, primary_key=True, nullable=False)

    # Text Column Schema
    text = DB.Column(DB.Unicode(300), nullable=False)

    # User Column Schema
    # (this is how we add a secondary / foreign key)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey(
        'user.id'), nullable=False)
    # (this will automatically create the one-many relationship,
    #  but also adds a new attributes onto the "User" called "tweets"
    #  which will be a list of all of the user tweets)
    user = DB.relationship("User", backref=DB.backref('tweets'), lazy=True)
    # (lazy just means that it won't be created until accessed)

    # Word Embeddings Vector Storage (vect for short)
    # A PickleType is any python object
    vect = DB.Column(DB.PickleType, nullable=False)
