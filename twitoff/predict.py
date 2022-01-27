from .models import User
from .twitter import vectorize_tweet
import numpy as np
from sklearn.linear_model import LogisticRegression


def predict_user(username0, username1, hypo_tweet_text):
    '''
    Determine and returns which user is more likely to say a given tweet
    Example run: predict_user("elonmusk", "jackblack", "Tesla cars go vroom")
    Returns a 0 (user0_name: "elonmusk") or a 1 (user1_name: "jackblack")
    '''

    # Query for the two users
    user0 = User.query.filter(User.username == username0).one()
    user1 = User.query.filter(User.username == username1).one()

    # Get the word embeddings
    vects0 = np.array([tweet.vect for tweet in user0.tweets])
    vects1 = np.array([tweet.vect for tweet in user1.tweets])

    # Combine the two users' word embeddings into one big 2D array
    # (X matrix for training logistic regression)
    vects = np.vstack([vects0, vects1])

    # Create a np array to represent the y vector
    labels = np.concatenate([
        np.zeros(len(user0.tweets)),
        np.ones(len(user1.tweets))
    ])

    # import and train out logistic regression
    log_reg = LogisticRegression()

    # train our logistic regression
    log_reg.fit(vects, labels)

    # Get the word embeddings for our hypo_tweet_text
    hypo_tweet_vect = vectorize_tweet(hypo_tweet_text)

    # Generate a prediction
    prediction = log_reg.predict([hypo_tweet_vect])

    return prediction[0]
