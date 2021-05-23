import config
import tweepy

def setupTwitterBot():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(config.Twitter_CONSUMER_KEY, config.Twitter_CONSUMER_SECRET)
    auth.set_access_token(config.Twitter_ACCESS_TOKEN, config.Twitter_ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    api.verify_credentials()
    print("Authentication OK")

    return api