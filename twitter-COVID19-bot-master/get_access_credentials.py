# If you have not run this program before, or if you are running it on a new account, please run get_access_credentials first
# and fill out the config.py

import tweepy
from tweepy import OAuthHandler

import COVID_bot
import config as config
import logging
from datetime import datetime as d
import datetime as dt
import sys
import argparse
import time
import _thread

import follow_twitter

# accounts_to_follow_from = ['Account1', 'Account2', 'Account3']

# # # Specify the username you would like to follow the followers of here # # #
username_to_follow_from = 'Account1'

def main1():
    # Check config file is ok
    if config.consumer_key != "" or config.consumer_secret != "" or config.access_token != "" or config.access_token_secret != "":
        consumer_key = config.consumer_key
        consumer_secret = config.consumer_secret
    else:
        print("Fill the config file please!")
        return

    # Auth process
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    # get access token from the user and redirect to auth URL
    auth_url = auth.get_authorization_url()

    print('Authorization URL: ' + auth_url)

    # ask user to verify the PIN generated in browser
    verifier = input('PIN: ').strip()
    auth.get_access_token(verifier)

    print("Please place the values below in the config.py file")
    print('ACCESS_TOKEN = "%s"' % auth.access_token)
    print('ACCESS_TOKEN_SECRET = "%s"' % auth.access_token_secret)

    # authenticate and retrieve user name
    auth.set_access_token(auth.access_token, auth.access_token_secret)
    api = tweepy.API(auth)
    username = api.me().name
    print('Connected to ' + username)
    # return auth.access_token, auth.access_token_secret

    # sys.exit()


def getAuth():
    # Check config file is ok
    if config.consumer_key != "" or config.consumer_secret != "" or config.access_token != "" or config.access_token_secret != "":
        consumer_key = config.consumer_key
        consumer_secret = config.consumer_secret
    else:
        print("Fill the config file please!")
        return
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    return auth


def getAuthURL(auth):
    auth_url = auth.get_authorization_url()
    return auth_url


def getAccessToken(auth, verifier, target_username, logger):
    #logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #                    datefmt='%m-%d %H:%M', level=logging.INFO, encoding="utf-8")

    auth.get_access_token(verifier)
    access_token = auth.access_token
    access_token_secret = auth.access_token_secret

    # print("Please place the values below in the config.py file")
    # print('ACCESS_TOKEN = "%s"' % auth.access_token)
    # print('ACCESS_TOKEN_SECRET = "%s"' % auth.access_token_secret)

    # authenticate and retrieve user name
    auth.set_access_token(auth.access_token, auth.access_token_secret)
    api = tweepy.API(auth)
    username = api.me().name
    logger.info(' Access Token: ' + str(auth.access_token) + ' Username: ' + str(username))
    # print('Connected to ' + username)

    # Uncomment the below line for he simple follow bot
    # follow_twitter.main(username, api, target_username, access_token, access_token_secret)
    logger.info('Transferring to COVID_bot...')
    COVID_bot.main(username, api, username_to_follow_from, access_token, access_token_secret, logger)
    # return access_token, access_token_secret


def setAuth(auth):
    # authenticate and retrieve user name
    auth.set_access_token(auth.access_token, auth.access_token_secret)
    api = tweepy.API(auth)
    username = api.me().name
    print('Connected to ' + username)


def main(auth, verifier, target_username, logger):
    getAccessToken(auth, verifier, target_username, logger)
    # setAuth

# if __name__ == "__main__":
#   main(auth, verifier, log_file)
