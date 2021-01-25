

import tweepy


def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)


def get_text_to_tweet():
    file_to_tweet = 'tweetToSend.txt'
    with open(file_to_tweet, 'r') as file:
        tweet = file.read()
        print(tweet)
    return tweet


def main():
    cfg = {
      "consumer_key": "fuuAgy3pElOz4Ecy4ZF1OSuRh",
      "consumer_secret": "7XZnEh5PwXHQ2AH8Ma52g41aAB0D2cTvDSbPaHnzErPSzDAnZt",
      "access_token": "1247287333478699008-KKpYUUHBBxDpJwudh525izgb1EZOVF",
      "access_token_secret": "ZDNOfmy2iV9dGNEce14Bgqym2g4j2cEhpibGaztv9GxVc"
    }

    api = get_api(cfg)
    tweet_to_send = get_text_to_tweet()

#    tweet = "Hello, world!"  # to send out a tweet
#    status = api.update_status(status=tweet)
    # Yes, tweet is called 'status' rather confusing

#    public_tweets = api.home_timeline(tweet_mode='extended')  # to get all tweets coming in
#    for tweet in public_tweets:
#        print(tweet)

# open and read in file to tweet out
    # TODO put the temperature in a txt file



#  send out the tweet
    status = api.update_status(status=tweet_to_send)



if __name__ == "__main__":
    main()
