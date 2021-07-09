# https://realpython.com/twitter-bot-python-tweepy/
# Create The Ultimate Twitter Bot With Python In 30 Minute youtube


import tweepy

import weather_pi
from python_config import read_config
from datetime import datetime
from send_email import send_email
from WeatherAppLog import get_a_logger
import time

logger = get_a_logger(__name__)
logger.setLevel('INFO')


def get_api():
    cfg = read_config(section='twitter')
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    try:
        api.verify_credentials()
        print("Tweepy authentication OK")
    except Exception as e:
        print("error in authentication")
        raise e
    return api
# 1411772214538477569
# 1411531233817989121
def write_text_to_tweet(string, file_name='tweet_to_send.txt'):
  #  tempnow = dict_result['temp'][-1]
    with open(file_name, 'w') as file:
        file.write(string)
    return


def read_text_to_tweet(file_name='tweet_to_send.txt'):
    with open(file_name, 'r') as file:
        text = file.read()
    return text


def read_last_tweet_seen(file_name='last_tweet_seen.txt'):
    with open(file_name, 'r') as file_read:
        last_seen_id = int(file_read.read().strip())
    return last_seen_id


def write_last_tweet_seen(last_seen_id, file_name='last_tweet_seen.txt'):
    with open(file_name, 'w') as file_write:
        file_write.write(str(last_seen_id))
    return


def send_reply_tweet(api):
    """
    if NEW tweet mentions me (WeatherDavid) and #weather then
    like it
    reply back to that person with current temperature_tweet
    Args:
        api ():

    Returns:

    """
    # api = get_api()
    mentions = api.mentions_timeline(since_id=read_last_tweet_seen(), tweet_mode='extended')  # get all tweets that mention me
    for tweet in reversed(mentions):
        if '#weather' in tweet.full_text.lower():
            print(f"ID: {tweet.id} , text: {tweet.full_text} {tweet.user.screen_name}")
            try:
                # status_a = read_text_to_tweet(file_name='temperature_tweet.txt')  # this posts as tweet
                status = f"@{tweet.user.screen_name} {read_text_to_tweet(file_name='temperature_tweet.txt')} #Weather"
                write_last_tweet_seen(tweet.id)
                api.update_status(status, in_reply_to_status_id=tweet.id)
                api.create_favorite(tweet.id)  # 'like' it
                # api.retweet(tweet.id)  # this retweets, don't think really need to retweet
            except tweepy.TweepError as e:
                logger.error(f"Tweet error: {e.reason}")
                print(e.reason)
                send_email(subject="Tweet error", message=f"ERROR: {e.reason}")
    # print('send reply done')
    return


def send_new_tweet(file):
    api = get_api()
    tweet_to_send = read_text_to_tweet(file)
    try:
        status = api.update_status(status=tweet_to_send)
    except tweepy.TweepError as e:
        logger.error(f"Tweet error: {e.reason}")
        send_email(subject="Tweet Error", message=f"Tweet error: {e.reason}")
    return


def send_new_dm(file):
    api = get_api()
    tweet_to_send = read_text_to_tweet(file)
    try:
        status = api.send_direct_message(recipient_id='DavidDoc', text=tweet_to_send)
    except tweepy.TweepError as e:
        logger.error(f"Tweet error: {e.reason}")
        send_email(subject="Tweet Error", message=f"Tweet error: {e.reason}")
    return


def get_incoming_tweets(api, hashtag='#arwx -#WPS -#razorbacks -#ProHogs', number_tweets=10):
    """
    get new tweets since last seen tweet
    if not following
    follow and retweet
    Args:
        api ():
        hashtag ():
        number_tweets ():

    Returns:

    """
    # api = get_api()
    # tweets = tweepy.Cursor(api.search, hashtag).items(number_tweets)
    tweets = tweepy.Cursor(api.search, q=hashtag,
                           tweet_mode="extended").items(number_tweets)

    for tweet in tweets:
        print('---------------')
        print(tweet.full_text)

        stweet = api.get_status(tweet.id)
        # print('tweet')
        if stweet.retweeted is False:
            # print(tweet.retweeted)
            if stweet.user.screen_name != 'WeatherDavid':
                print(f"liked and retweeted: {tweet.user.screen_name}")
                tweet.retweet()
                api.create_favorite(tweet.id)
                if not tweet.user.following:
                    print(tweet.user.following)
                    api.create_friendship(tweet.user.screen_name)
                    print(f"friended / followed : {tweet.user.screen_name}")
                    # self.api.create_favorite(tweet.id)
                # tweet.retweet()
                # print('retweeted')

    print('get incoming done')
    return tweets


def send_retweet(tweets):
    # get_api()
    for tweet in tweets:
        try:
            tweet.retweet()
            time.sleep(2)
            # print('tweet resent')
        except tweepy.TweepError as te:
            print(te.reason)
            time.sleep(2)
    print('retweet done')
    return


def follow_followers(api):
    """
    check all users that are following me
    if I am not following them
    follow them
    send message
    not run often
    Returns:

    """
    # print('statrt follower')
    # api = get_api()
    for follower in tweepy.Cursor(api.followers).items():
        # print(follower.following)
        # print(follower.screen_name)
        if not follower.following:
            follower.follow()
            status = f"@{follower.screen_name} Thanks for following, if you want to know the temperature in Little Rock mention me in a tweet and use hashtag #weather."
            # print(status)
            api.update_status(status=status)
    # print('follow done')


def main():
    api = get_api()  # based on config.ini

    # tweets = get_incoming_tweets(api)

    while True:
        # follow_followers(api)
        send_reply_tweet(api)
        # time.sleep(6)
        tweets = get_incoming_tweets(api)
        # send_retweet(tweets)
        time.sleep(600)




if __name__ == "__main__":
    main()
