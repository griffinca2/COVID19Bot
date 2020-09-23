# Application Development Plan
# Following function to take care of the following users
# Tweet function to tweet to the account
# Scraping function to scrape the new relevant info from website

# TODO: Need two threads:
# One for the twitter follower
# One for the Tweet poster/scraper

import follow_twitter
import logging
import threading
import twitter_post
from datetime import datetime as d
import datetime as dt
import time

# Specify the usernames of acounts to follow users from here, separated by commas.
# accounts_to_follow_from = ['Account1', 'Account2', 'Account3']


# def main(username, api, target_username, access_token, access_token_secret):
def main(username, api, target_username, access_token, access_token_secret, logger):
    # if __name__ == '__main__':
    # format = "%(asctime)s: %(message)s"
    # logging.basicConfig(format=format, level=logging.INFO,
    #                        datefmt="%H:%M:%S")
    # logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #                    datefmt='%m-%d %H:%M', level=logging.INFO, encoding="utf-8")

    logger.info('Main...')
    # TODO: Comment out tf for testing. Uncomment tf for Live
    logger.info("Main    : before creating thread")
    tf = threading.Thread(target=follow_twitter.main,
                          args=(username, api, target_username, access_token, access_token_secret, logger,))
    tf.daemon = True
    tp = threading.Thread(target=twitter_post.main, args=(api, logger,))
    tp.daemon = True
    logger.info("Main    : before running thread")
    tf.start()
    tp.start()
    tp.join()
    logger.info("Main    : all done")

    # follow_twitter.main(username, api, target_username, access_token, access_token_secret)

    # else:
    # logging.info('Not main...')
    # print('Not main...')
