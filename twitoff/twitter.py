from os import getenv
import tweepy
import spacy
from .models import DB, Tweet, User

# for testing: flask shell lets you create a python REPL with access to environment variables

# Get our API keys from our .env file
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

# Connect to the Twitter API
# 1) Authenticate
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
# 2) Open Connection to Twitter API
TWITTER = tweepy.API(TWITTER_AUTH)


def add_or_update_user(username):

    try:  # this is to ensure atomicity
        twitter_user = TWITTER.get_user(screen_name=username)

        # Is this user already in our DB?
        # If so, then just update
        db_user = (User.query.get(twitter_user.id) or User(
            id=twitter_user.id, username=username))
        # This evaluates left to right where the right side will only be run if the LHS query
        # statement returns false (python treats does not exist or empty as false)

        DB.session.add(db_user)

        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)
        # since_id gets all of user's tweets since the tweet with that id

        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # We created the folder 'my_model'
        # nlp = spacy.load('en_core_web_sm')
        # nlp.to_disk('my_model')

        # Loop over tweets and insert them into DB 1 by 1
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:300],
                             user_id=db_user.id,
                             vect=tweet_vector)
            DB.session.add(db_tweet)

    except Exception as error:
        print(f'Error When Processing {username}: {error}')
        raise error

    else:
        DB.session.commit()


nlp = spacy.load('my_model/')


def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector
