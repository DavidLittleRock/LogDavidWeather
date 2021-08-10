# https://realpython.com/twitter-bot-python-tweepy/
# Create The Ultimate Twitter Bot With Python In 30 Minute youtube


import tweepy

# import weather_pi
from python_config import read_config
from datetime import datetime
# from send_email import send_email
from WeatherAppLog import get_a_logger
import time
import schedule

logger = get_a_logger(__name__)
logger.setLevel('DEBUG')


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
    with open(file_name, 'w') as file:
        file.write(string)
    logger.info('write_text_to_tweet')
    logger.debug('write_text_to_tweet;\n\tstring: %s\n\tfile name: %s', string, file_name)


def read_text_to_tweet(file_name='tweet_to_send.txt'):
    with open(file_name, 'r') as file:
        text = file.read()
    logger.info('start')
    logger.debug('read_text_to_tweet;\n\tfile name: %s\n\ttext: %s', file_name, text)
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
    """
    if NEW tweet mentions me (WeatherDavid) and #weather then
    like it
    reply back to that person with current temperature_tweet
    Args:
        api ():

    Returns:

    """
    api = get_api()
    mentions = api.mentions_timeline(since_id=read_last_tweet_seen(), tweet_mode='extended')  # get all tweets that mention me
    for tweet in reversed(mentions):
        if '#weather' in tweet.full_text.lower():  # extract tweets with hashtag weather
            logger.debug('MENTIONED in tweet id: %s\n\ttext: %s\n\tuser screen name: %s',tweet.id, tweet.full_text, tweet.user.screen_name)
            try:
                status = f"@{tweet.user.screen_name} {read_text_to_tweet(file_name='reply_tweet.txt')} #Weather"
                if read_last_tweet_seen() < tweet.id:  # update last tweet seen
                    write_last_tweet_seen(tweet.id)
                if tweet.user.screen_name != api.me().screen_name:  # if tweet not sent by me
                    api.update_status(status, in_reply_to_status_id=tweet.id)
                    if not api.get_status(tweet.id).favorited:  # id I have not liked tweet yet
                        api.create_favorite(tweet.id)  # 'like' it
                    print(f"so I like their tweet and reply with: \n\t@{tweet.user.screen_name} {read_text_to_tweet(file_name='reply_tweet.txt')} #Weather")
                # api.retweet(tweet.id)  # this retweets, don't think really need to retweet
            except tweepy.TweepError as e:
                logger.error(f"Tweet error: {e.reason}")
                print(e.reason)
                # send_email(subject="Tweet error", message=f"ERROR: {e.reason}")
    return


def send_new_tweet(file):
    api = get_api()
    tweet_to_send = read_text_to_tweet(file)
    try:
        status = api.update_status(status=tweet_to_send)
    except tweepy.TweepError as e:
        logger.error('Tweet error: %s', e.reason)
        # send_email(subject="Tweet Error", message=f"Tweet error: {e.reason}")
    return


def send_text_tweet(text):
    api = get_api()
    tweet_to_send = text
    try:
        status = api.update_status(status=tweet_to_send)
    except tweepy.TweepError as e:
        logger.error('Tweet error: %s', e.reason)
        # send_email(subject="Tweet Error", message=f"Tweet error: {e.reason}")
    return

def send_new_dm(file):
    api = get_api()
    tweet_to_send = read_text_to_tweet(file)
    try:
        status = api.send_direct_message(recipient_id='DavidDoc', text=tweet_to_send)
    except tweepy.TweepError as e:
        logger.error(f"Tweet error: {e.reason}")
        # send_email(subject="Tweet Error", message=f"Tweet error: {e.reason}")
    return


def get_incoming_tweets(hashtag='#arwx -#WPS -#razorbacks -#ProHogs', number_tweets=5):
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
    api = get_api()
    tweets = tweepy.Cursor(api.search, q=hashtag,
                           tweet_mode="extended", since_id=read_last_tweet_seen(file_name='last_tweet_seen.txt')).items(number_tweets)
    for tweet in tweets:
        if read_last_tweet_seen() < tweet.id:
            write_last_tweet_seen(tweet.id)
        try:
            stweet = api.get_status(tweet.id)

            if stweet.user.screen_name != api.me().screen_name:  # if not me
                if not tweet.user.following:  # if I am not following
                    try:
                        api.create_friendship(tweet.user.screen_name)
                        print(f'friended / followed: {tweet.user.screen_name}')
                    except tweepy.TweepError as e:
                        print(e)
                if stweet.retweeted is False:  # if not allready retweeted
                    tweet.retweet()
                    print('retweeted')
                if not stweet.favorited:  # if I have not liked yet
                    api.create_favorite(tweet.id)
                    print('liked')
        except tweepy.TweepError as e:
            print(e)
            print(f'blocked by {tweet.user.screen_name}')
    return tweets


def send_retweet(tweets):
    # get_api()
    for tweet in tweets:
        try:
            tweet.retweet()
            time.sleep(2)
        except tweepy.TweepError as te:
            print(te.reason)
            time.sleep(2)
    print('retweet done')
    return


def follow_followers():
    """
    check all users that are following me
    if I am not following them
    follow them
    send message
    not run often
    Returns:

    """
    api = get_api()
    for follower in tweepy.Cursor(api.followers).items(5):
        if not follower.following:
            follower.follow()
            status = f"@{follower.screen_name} Thanks for following my bot, if you want to know the temperature in Little Rock mention me in a tweet and use hashtag #weather. May take 5 min to respond."
            api.update_status(status=status)


def main():
    api = get_api()  # based on config.ini
    # tweets = get_incoming_tweets(api)
    schedule.every(2).minutes.do(send_reply_tweet)
    schedule.every(10).minutes.do(follow_followers)
    schedule.every(15).minutes.do(get_incoming_tweets)
    while True:
        schedule.run_pending()
        time.sleep(2)


    print('0')
  #  send_reply_tweet(api)
    print('1')

    # follow_followers(api)
 #   send_reply_tweet(api)
    print('2')
#        # time.sleep(6)
    # tweets = get_incoming_tweets(api)
    print('3')
        # send_retweet(tweets)
        # time.sleep(300)




if __name__ == "__main__":
    main()
