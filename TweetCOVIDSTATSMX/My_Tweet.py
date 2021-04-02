import tweepy as tw 
import os
import json
class My_Tweet:
    def post (info,pathImage):
        # Get credentials froma a json file
        mainpath = "../../TweetApiCredentials"
        filepath = "TwitterApiKeys.json"
        with open(os.path.join(mainpath,filepath)) as file:
            credentials = json.load(file)
        
        key_1 = credentials['key_1']
        key_2 = credentials['key_2']
        key_3 = credentials['key_3']
        key_4 = credentials['key_4']
        # Authenticate to Twitter
        auth = tw.OAuthHandler(key_1, key_2 )
        auth.set_access_token(key_3, key_4 )

        # Create API object
        api = tw.API(auth, wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True)
        media = api.media_upload("Graficas/"+pathImage)     #2020-10-14/NACIONAL.png")
        # Post tweet with image
        tweet = info
        post_result = api.update_status(status=tweet, media_ids=[media.media_id])

My_Tweet.post = staticmethod(My_Tweet.post)

