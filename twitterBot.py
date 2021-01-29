

import tweepy
from python_config import read_config
from datetime import datetime


def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth, wait_on_rate_limit=True)


def get_text_to_tweet():
    file_to_tweet = 'tweetToSend.txt'
    with open(file_to_tweet, 'r') as file:
        tweet = file.read()
        print(tweet)
    return tweet


def read_lastTweetSeen(file_name='lastTweetSeen.txt'):
    with open(file_name, 'r') as file_read:
        last_seen_id = int(file_read.read().strip())
    return last_seen_id


def write_lastTweetSeen(last_seen_id, file_name='lastTweetSeen.txt'):
    with open(file_name, 'w') as file_write:
        file_write.write(str(last_seen_id))
    return


def reply():
    cfg = read_config(section='twitter')

    api = get_api(cfg)

    mentions = api.mentions_timeline(since_id=read_lastTweetSeen(), tweet_mode='extended')  # get all tweets that mention me

    for tweet in reversed(mentions):
        if '#weather' in tweet.full_text.lower():
            print(f"ID: {tweet.id} , text: {tweet.full_text}")
            try:
                api.update_status(f"at {datetime.now()} @{tweet.user.screen_name} reply tweet, here; #weather", tweet.id)
                api.create_favorite(tweet.id)
                api.retweet(tweet.id)
                write_lastTweetSeen(tweet.id)
            except tweepy.TweepError as e:
                print(e.reason)

def new_tweet():
    cfg = read_config(section='twitter')

    api = get_api(cfg)
    tweet_to_send = get_text_to_tweet()
    status = api.update_status(status=tweet_to_send)


def main():
    reply()
#    cfg = read_config(section='twitter')

#    api = get_api(cfg)
 #   tweet_to_send = get_text_to_tweet()

#    tweet = "Hello, world!"  # to send out a tweet
#    status = api.update_status(status=tweet)
    # Yes, tweet is called 'status' rather confusing

#    public_tweets = api.home_timeline(tweet_mode='extended')  # to get all tweets coming in
#    for tweet in public_tweets:
#        print(tweet)

# open and read in file to tweet out
    # TODO put the temperature in a txt file

#    mentions = api.mentions_timeline(since_id=read_lastTweetSeen(), tweet_mode='extended')  # get all tweets that mention me


 #       for tweet in reversed(mentions):
 #           if '#weather' in tweet.full_text.lower():
 #               print(f"ID: {tweet.id} , text: {tweet.full_text}")
 #               api.update_status(f"at {datetime.now()} @{tweet.user.screen_name} reply tweet, here; #weather", tweet.id)
 #               api.create_favorite(tweet.id)
  #              api.retweet(tweet.id)
  #              write_lastTweetSeen(tweet.id)




   # print(mentions[0].entities['hashtags'][0]['text'])

#  send out the tweet
#    status = api.update_status(status=tweet_to_send)



if __name__ == "__main__":
    main()
