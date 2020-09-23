# coding=utf-8
import os

# Application Development Plan
# Following function to take care of the following users
# Tweet function to tweet to the account
# Scraping function to scrape the new relevant info from website

import tweepy
from tweepy import OAuthHandler
import config as config
import time
import random
# import random.choices
from tkinter import *
import twitterScroller
import logging

from datetime import datetime as d
import datetime as dt
import get_access_credentials

# import pymongo

# Default limit of tweets
def_limit = 5
delay_ = 1

# Setting Defaults - Future: Make all settings below customisable.
# TODO: Follow 2-4 user per operation - ✓
# TODO: Follow 100 - 120 users per day - ✓
# TODO: Do not follow private users ✓
# TODO: Follow random users from the list - In the future, do with MongoDB. Immediate solution it to store in list. ✓
# TODO: Wait 35 - 60 minutes before each new operation - ✓
# TODO: Check if user has already been followed - ✓
# TODO: Scroll the search page for 120 seconds per day - In progress
# TODO: Follow active users - that have retweeted/liked posts of target account
#       - follow user with more than ?50? tweets ✓
#       - follow users that have favorited a certain number of main user's tweets
#       - follow users that have commented on a certain number of main user's tweets
#       - follow users that have retweeted a certain number of main user's tweets - ✓ - DONE, but goes over API limits
#       - follow users with at least 1 tweet within 1 week - ✓
# TODO: Like latest posts of user after follow [Like between 1 and 3 posts] - like percentage 80 % - ✓


# Max and min number for users to follow per operation
min_users = 2
max_users = 4

# Max and Min for minutes to wait between operations
min_minutes = 0#35
max_minutes = 1#60

# Max and min number of follows to do per 24 hr period
min_follows = 100
max_follows = 120

# Max and min number of tweets to like
min_likes = 1
max_likes = 3

# Amount of time to scroll on the search page
scroll = 120

num_followed = 0

followers_list = []

start_time = time.time()


# # # # # # # # # # # # # # # # HELPER FUNCTIONS START # # # # # # # # # # # # # # # #

def rateLimit():
    print("Rate limit. Waiting for 2 minutes and trying again.")
    logging.info("Rate limit. Waiting for 2 minutes and trying again.")
    print("If it fails again, try to regenerate Twitter Keys and Tokens")
    logging.info("If it fails again, try to regenerate Twitter Keys and Tokens")
    time.sleep(120)
    return


# Gets a random number between min_users and max_users. This is the number of users to follow per operation
def getUsersPerOp():
    return random.randrange(min_users, max_users)


# Gets a random number between min_minutes and max_minutes. This is the time between operations
def getMinBetweenOp():
    return random.randrange(min_minutes, max_minutes) * 60


# Gets a random number between min_follows and max_follows. This is the total number of users to follow in one day
def getNumUsersToFollow():
    return random.randrange(min_follows, max_follows)


# TODO This is the function to mimic scrolling on the search page. Still needs to be implemented.
def scrollSearchPage():
    twitterScroller.scroll()


# TODO Function to check how active the user is. Calculates an activity score.
# user = user who's activity is being evaluated. username = username of user who's followers are being evaluated
# So far, min = 1 & max = 8
def getActivityScore(api, username, user, logger):
    activity_score = 0
    nt_score = getNumTweetsScore(api, username, logger)
    if nt_score > 0:
        t_in_week = int(tweetedInWeek(api, username, logger))
        # num_retweeted = getNumberRetweeted(api, user, username)

        activity_score = nt_score + t_in_week  # + num_retweeted
    else:
        activity_score = 0
    #print("Activity Score = " + str(activity_score))
    logger.info("Activity Score = " + str(activity_score))
    return activity_score


#  Get total number of tweets a user has. Value is factored into activity score
def getNumTweetsScore(api, screenName, logger):
    numTweets = api.get_user(screenName).statuses_count
    #print("The user " + str(screenName) + " has " + str(numTweets) + " Tweets.")
    logger.info("The user " + str(screenName) + " has " + str(numTweets) + " Tweets.")

    if (numTweets == 0):
        nt_score = 0
    elif (numTweets < 50 and numTweets > 0):
        nt_score = 1
    elif (numTweets < 100 and numTweets >= 50):
        nt_score = 2
    elif (numTweets < 250 and numTweets >= 100):
        nt_score = 3
    elif (numTweets < 500 and numTweets >= 250):
        nt_score = 4
    else:
        nt_score = 5
    return nt_score


def likeLatestTweets(api, user, logger):
    # u = api.get_user(user).user_id
    ran = random.randrange(min_likes, max_likes)
    i = 0
    # while i < ran:
    tweets = api.user_timeline(id=user, count=ran, tweet_mode='extended')
    for tweet in tweets:
        # tweet = api.user_timeline(id=user, count=ran, tweet_mode='extended')[i]
        #print("Passed tweet: " + str(tweet.id))
        logger.info("Passed tweet: " + str(tweet.id))
        # print(api.statuses_lookup([tweet.id]))
        # logging.info(api.statuses_lookup([tweet.id]))
        if not isFavorited(api, user, tweet.id):
            api.create_favorite(tweet.id)
            #print("Favorited: " + str(tweet.id))
            logger.info("Favorited: " + str(tweet.id))

        # try:
        #    twt = api.statuses_lookup([tweet.id])
        #    if not twt.favorited:
        #        api.create_favorite(tweet[i].id)
        #       print("Favorited: " + str(tweet[i].text))
        #        logging.info("Favorited: " + str(tweet[i].text))
        # except tweepy.TweepError as e:
        #    print(str(e))
        #    logging.info(str(e))
        #    pass


# Function to choose whether or not to like a user's Tweets. Returns 'True' or '1' 80% of the time
def doLike():
    population = [0, 1]
    ch = random.choices(population, weights=[0.2, 0.8])
    return ch[0]


# TODO Function to unfollow users that do not follow you back. Not used currently. To be used and
# implemented in the future
def unfollow(api, logger):
    for page in tweepy.Cursor(api.friends, count=100).pages():
        user_ids = [user.id for user in page]
        for relationship in api._lookup_friendships(user_ids):
            if not relationship.is_followed_by:
                logger.info('Unfollowing @%s (%d)',
                             relationship.screen_name, relationship.id)
                try:
                    api.destroy_friendship(relationship.id)
                except tweepy.error.TweepError:
                    logger.info('Error unfollowing.')


# Function to check if the user is already followed
def isFollowed(api, user_a, user_b, logger):
    user_name = api.get_user(user_b).screen_name
    # print('User:' + str(user_name))
    relationship = api.show_friendship(source_id=user_a, target_id=user_b)
    # relationship = api.lookup_friendships(screen_name=[api.get_user(user).screen_name])
    # Check if you are already following the user
    # print("Relationship[0] = " + str(relationship[0]))
    #print("Is the user  " + str(user_name) + ' already followed?  ' + str(relationship[0].following))
    logger.info("Is the user  " + str(user_name) + ' already followed?  ' + str(relationship[0].following))
    return relationship[0].following


# Check if the user has tweeted in the last week
def tweetedInWeek(api, user, logger):
    answer = False
    tweet = api.user_timeline(id=user, count=1)[0]
    tweet_date = dt.datetime.strptime(str(tweet.created_at), "%Y-%m-%d  %H:%M:%S")
    now = dt.datetime.now()
    delta = now - tweet_date
    if delta.days < 7:
        answer = True
        #print("User has tweeted in the past week: " + str(answer))
        logger.info("User has tweeted in the past week: " + str(answer))
    return answer


# Checks if a tweet has been favorited
# Get authenticating user's favorites. Check if current tweet is in them.
def isFavorited(api, user, currentTweetID):
    # Get authenticating user's favorites(max 200).
    favorites = api.favorites(user_id=user, count=200)
    # For each status in the favorites list, check if the status' id matches the current status_
    # id we're trying to favorite
    for status in favorites:
        if status == currentTweetID:
            #print("Tweet has already been favorited.")
            logging.info("Tweet has already been favorited.")
            return True
    return False


# Finds out how many of the original account's recent Tweets a following user has retweeted
def getNumberRetweeted(api, user_orig, user_in_question):
    a = 0
    retweeted_score = 0
    id_in_question = api.get_user(user_in_question).id
    for tweet in api.user_timeline(id=user_orig, count=10):
        # print("TWEET:", tweet.text)
        for reTweet in api.retweets(tweet.id):
            if reTweet.id == id_in_question:
                a += 1
                # print("USER has retweeted:", reTweet.user.screen_name)
                # print("USER has retweeted the original account " + str(a) + ' times.')
    if a < 5:
        retweeted_score = 1
    elif a < 25 and a >= 5:
        retweeted_score = 2
    elif a < 75 and a >= 25:
        retweeted_score = 3
    else:
        retweeted_score = 4
    return retweeted_score


# # # # # # # # # # # # # # # # HELPER FUNCTIONS END # # # # # # # # # # # # # # # #


def operations(api, username, target_username, logger):
    # Get the number of follows to do in one 24 hr period
    num_follows_24hr = getNumUsersToFollow()
    #print("Total number of follows to do in 24 hrs: " + str(num_follows_24hr))
    logger.info("Total number of follows to do in 24 hrs: " + str(num_follows_24hr))

    # Get total number of followers the target account has
    followers_list = getFollowers(api, target_username, logger)
    total_follows = len(followers_list)
    #print("operations(): the number of followers the target account has is:" + str(total_follows))
    logger.info("operations(): the number of followers the target account has is:" + str(total_follows))
    # Sets the number of people followed to 0 before the following process begins
    num_followed = 0
    i = 0

    # time_elapsed = time.time() - start_time
    # print("Time elapsed: " + str(time_elapsed))

    # Track if we have followed all of the target account's followers. Can probably be done in a more efficient way.
    # TODO need to look at again later to improve efficiency
    while i < total_follows:
        # Track if we have gone over 24 hrs yet
        if num_followed < num_follows_24hr:
            users_per_op = getUsersPerOp()

            # Call the follow() function to follow users
            follow(api, users_per_op, target_username, logger)
            i += users_per_op

            # Increment the num_followed by the number of people just followed
            num_followed += users_per_op
            #print('# users followed this cycle: ' + str(users_per_op) + ' # number of users followed so far: ' + str(
                #num_followed))
            logger.info(
                '# users followed this cycle: ' + str(users_per_op) + ' # number of users followed so far: ' + str(
                    num_followed))

            if i >= total_follows:
                return

            min_betw_op = getMinBetweenOp()
            #print("Waiting " + str(min_betw_op / 60) + " minutes at " + str(time.time()))
            logger.info("Waiting " + str(min_betw_op / 60) + " minutes at " + str(time.time()))
            time.sleep(min_betw_op)
        else:
            # Check that the time is less than 24 hrs, and wait until the 24 hrs is over to restart.
            if time.time() - start_time < 86400:
                sleep_time = 86400 - (time.time() - start_time)
                #print("Number followed is over the 24 hr limit. Sleeping " + str(sleep_time) + " seconds")
                logger.info("Number followed is over the 24 hr limit. Sleeping " + str(sleep_time) + " seconds")
                time.sleep(sleep_time)
    print("Program finished.")
    return


def follow(api, users_per_op, username, logger):
    followers_list_hold = getFollowers(api, username, logger)
    i = 0
    while i < users_per_op:
        user = random.choice(followers_list_hold)
        #print("Current number of user in Op: " + str(i))
        logger.info("Current number of user in Op: " + str(i))
        my_id = api.me().id
        #print(str(my_id) + ' ' + str(user))
        logger.info(str(my_id) + ' ' + str(user))

        # Check if the user is already followed. This will save on API calls and time
        alreadyFollowed = isFollowed(api, my_id, user, logger)
        user_name = api.get_user(user).screen_name
        if alreadyFollowed:
            logger.info("User " + str(user_name) + "has already been followed: " + str(alreadyFollowed))
            #print(("User " + str(user_name) + "has already been followed: " + str(alreadyFollowed)))
            i += 1

        # If user has not been followed, get their activity score and check if their account is protected
        else:
            logger.info("User " + str(user_name) + " is not already followed. Following: " + str(alreadyFollowed))
            #print("User " + str(user_name) + " is not already followed. Following: " + str(alreadyFollowed))

            # Check if the user is protected. If so, do not follow.
            if not api.get_user(user).protected:

                #print("User is not protected account. Protected status: " + str(api.get_user(user).protected))
                logger.info("User is not protected account. Protected status: " + str(api.get_user(user).protected))

                # Get the Activity Score of the user.
                act_score = getActivityScore(api, user, username, logger)

                # Check if the user has an activity score greater than 2.
                if act_score >= 2:
                    # Follow the user
                    api.create_friendship(user)
                    #print(user_name + ' has been followed.')
                    logger.info(user_name + ' has been followed.')

                    # Make sure the most recent tweets are liked only 80% of the time
                    a = doLike()
                    # print("Like or do not like: " + str(a))
                    if a == 1:
                        # Like the users most recent tweets(random number between 2 and 5)
                        likeLatestTweets(api, user, logger)
                    else:
                        #print("Tweets not liked.")
                        logger.info("Tweets not liked.")

                    # print(" Actual following turned off currently. Followed - " + str(api.get_user(user).screen_name))
                    #print("Followed - " + str(api.get_user(user).screen_name))
                    logger.info("Followed - " + str(api.get_user(user).screen_name))
                else:
                    #print("User has activity score less than 2. Not followed.")
                    logger.info("User has activity score less than 2. Not followed.")
            else:
                #print("User has a protected account. Protected status: " + str(api.get_user(user).protected))
                logger.info("User has a protected account. Protected status: " + str(api.get_user(user).protected))

            # TODO: Uncomment the below
            wait1 = random.randrange(240, 480)
            #wait1 = random.randrange(5, 10)

            #print("Waiting: " + str(wait1))
            logger.info("Waiting: " + str(wait1))
            time.sleep(wait1)
            # remove the followed user from the follow list
            #print("Removed user " + str(user) + " from the list.")
            logger.info("Removed user " + str(user) + " from the list.")
            followers_list_hold.remove(user)
        i += 1


def getFollowers(api, username, logger):
    # Follow the followers of a user
    #print("Creating a list of followers for the user: " + username)
    logger.info("Creating a list of followers for the user: " + username)
    followers = []
    try:
        followers = api.followers_ids(screen_name=username)
    except tweepy.TweepError as e:
        print("Going to sleep:", e)
        time.sleep(60)
        sys.exit()
    return followers


# Checks the auth keys given on the config.py file, and then uses them to access Twitter API. Not using in V1 of
# standalone application
def connectToTW(user_id, access_token, access_token_secret, logger):
    username = user_id

    # Check config/auth details are ok
    # If config.consumer_key != "" or config.consumer_secret != "" or config.access_token != "" or config.access_token_secret != "":
    if config.consumer_key != "" or config.consumer_secret != "" or access_token != "" or access_token_secret != "":
        consumer_key = config.consumer_key
        consumer_secret = config.consumer_secret
        # access_token = config.access_token
        # access_token_secret = config.access_token_secret
    else:
        #print("Fill the config file please!")
        logger.info("Fill the config file please!")
        return
    # Auth process
    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
    except ValueError:
        #print("Error authenticating!")
        logger.info("Error authenticating!")
        sys.exit()
    u = api.me().name
    #print("Connected to: " + str(u))
    logger.info("Connected to: " + str(u))

    # Call operations function and start the following process
    # follow_twitter.main(api, username)
    # return api, username,
    # operations(api, username)


def main(username, api, target_username, access_token, access_token_secret, logger):
    #print("Connected to: " + str(username))
    #print("Target username: " + str(target_username))
    #path = 'Users/cag36/Desktop/GitHub Projects/_Twitter/twitter-followers-bot-master/logs'
    file_name = 'app' + d.now().strftime('%Y_%m_%d_%H_%M%S') + '.log'
    #filename = (os.path.join(path, file_name))
    #logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #                    datefmt='%m-%d %H:%M', level=logging.INFO)


    # connectToTW(username)
    # connectToTW(username, access_token, access_token_secret)

    operations(api, username, target_username, logger)
