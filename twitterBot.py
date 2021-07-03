# https://realpython.com/twitter-bot-python-tweepy/
# Create The Ultimate Twitter Bot With Python In 30 Minute youtube


import tweepy
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


def send_reply_tweet():
    api = get_api()
    mentions = api.mentions_timeline(since_id=read_last_tweet_seen(), tweet_mode='extended')  # get all tweets that mention me
    for tweet in reversed(mentions):
        if '#weather' in tweet.full_text.lower():
            print(f"ID: {tweet.id} , text: {tweet.full_text} {tweet.user.screen_name}")
            try:
                status_a = read_text_to_tweet(file_name='temperature_tweet.txt')  # this posts as tweet
                status = f"{status_a} @{tweet.user.screen_name} #Weather"
                write_last_tweet_seen(tweet.id)
                api.update_status(status, in_reply_to_status_id=tweet.id)
                api.create_favorite(tweet.id)
                api.retweet(tweet.id)  # this retweets
            except tweepy.TweepError as e:
                logger.error(f"Tweet error: {e.reason}")
                print(e.reason)
                send_email(subject="Tweet error", message=f"ERROR: {e.reason}")
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


def get_incoming_tweets(api, hashtag='#weather', number_tweets=2):
    # api = get_api()
    tweets = tweepy.Cursor(api.search, hashtag).items(number_tweets)
    # print(len(tweets))
    return tweets


def send_retweet(tweets):
    # get_api()
    for tweet in tweets:
        try:
            if not tweet.retweeted:
                tweet.retweet()
                time.sleep(2)
                print('tweet resent')
        except tweepy.TweepError as te:
            print(te.reason)
            time.sleep(2)
    return


def follow_followers():
    api = get_api()
    for follower in tweepy.Cursor(api.followers).items():
        # print(follower)
        if not follower.following:
            follower.follow()

def main():
    api = get_api()  # based on config.ini

    tweets = get_incoming_tweets(api)
    print(len(tweets))
    #for tweet in tweets:
    #    print(tweet.id)
    #    print(f"{tweet.user.screen_name} said {tweet.text}")
    #    try:
    #        tweet.retweet()
    #    except tweepy.TweepError as te:
    #        print(te.reason)

    # follow_followers()
    send_retweet(tweets)

#    send_new_dm(file='tweet_to_send.txt')
    #send_reply_tweet()
    # search_bot(tweets)
#   tweet_to_send = get_text_to_tweet()
    tweet = f"Hello, world! {datetime.now()}"  # to send out a tweet
   # status = api.update_status(status=tweet)
# Yes, tweet is called 'status' rather confusing
#    public_tweets = api.home_timeline(tweet_mode='extended')  # to get all tweets coming in
#    for tweet in public_tweets:
#        print(tweet)
# open and read in file to tweet out
   # TODO put the temperature in a txt file
#    mentions = api.mentions_timeline(since_id=read_last_tweet_seen(), tweet_mode='extended')  # get all tweets that mention me
#       for tweet in reversed(mentions):
#           if '#weather' in tweet.full_text.lower():
#               print(f"ID: {tweet.id} , text: {tweet.full_text}")
#               api.update_status(f"at {datetime.now()} @{tweet.user.screen_name} reply tweet, here; #weather", tweet.id)
#               api.create_favorite(tweet.id)
#              api.retweet(tweet.id)
#              write_last_tweet_seen(tweet.id)
# print(mentions[0].entities['hashtags'][0]['text'])

#  send out the tweet
#    status = api.update_status(status=tweet_to_send)



if __name__ == "__main__":
    main()
