#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
This Command line App stream new tweets from a given twitter's account

TODO: store tweets to files (with size limit) and/or to some Database (firebase/mongoDB alwaysdata?)
TODO: https://www.toptal.com/python/beginners-guide-to-concurrency-and-parallelism-in-python
'''

if __name__ == '__main__':

    import json
    import tweepy # Twitter mining/streaming lib
    import argparse # Command line the easy way
    from os import path as os_path
    from listener import StdOutListener
    from logger import super_logger
    from store import not_so_super_store

    #---------------------------------------------------
    # ARGPARSE
    #---------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Collect and store to disk the last $limit tweets from: $target's twitter account"
        +"see https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters"
        +"for more details on realtime tweets filters"
        )
    
    parser.add_argument('-f',"--follow",
        help="Collect only tweets that from a list of twitter users",default = "")

    parser.add_argument('-t',"--track",
        help="filter collected tweets with a list of keywords. No filter if not specified",default = "")

    parser.add_argument('-l', "--languages",
        help="maximum number of tweets to grab before closing stream. Default is 1",default = "")

    parser.add_argument("--tweets_limit",
        help="time limit in seconds. Default is 0 (no limit)", type=int, default=0)

    parser.add_argument("--time_limit",
        help="time limit in seconds. Default is 0 (no limit)", type=int, default=0)

    parser.add_argument("--loglvl",
        type=int,
        default=1,
        choices=[0,1,2,3,4,5],
        help="set the log level with an interger 0 to 5 :"
        +"{0: 'NONE', 1: 'DEBUG', 2: 'INFO', 3: 'WARN', 4: 'ERROR', 5: 'CRITICAL'}. Default is 1 (DEBUG)"
    )

    args = parser.parse_args()

    log = super_logger(log_lvl = args.loglvl)
    store = not_so_super_store()

    #---------------------------------------------------
    # Twitter Authentification
    #---------------------------------------------------
    # Import Twitter credentials from json file
    twitter_oauth_path = 'oauth.json'
    with open(twitter_oauth_path,'r', encoding='utf-8') as json_data:
        try:
            oauth_d = json.load(json_data)
            #log('info','{}'.format(oauth_d))
        except:
            log('critical','Error decoding json file with twitter credentials')
            exit(1)
        log(1, 'Twitter Credentials successfully imported from \"{}\"'.format(os_path.basename(twitter_oauth_path)))
    auth = tweepy.OAuthHandler(oauth_d["CONSUMER_KEY"], oauth_d["CONSUMER_SECRET"])
    auth.set_access_token(oauth_d["ACCESS_TOKEN"], oauth_d["ACCESS_TOKEN_SECRET"])

    #---------------------------------------------------
    # Get Twitter user_id from is is needed
    #---------------------------------------------------
    # https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-show
    # http://docs.tweepy.org/en/v3.5.0/api.html#user-methods

    api = tweepy.API(
        auth_handler = auth,
        retry_count=2,
        retry_delay=10,
        wait_on_rate_limit = True,
        wait_on_rate_limit_notify = True
        )

    if (not api):
        log('critical', 'Couldn\'t connect to the Twitter API')
        exit(1)

    if isinstance(args.follow, str):
        screen_name_list = [*args.follow.split()]
        log(1, 'Converting twitter screen_name(s) : '+str(screen_name_list))
        user_id_list = []
        for user_screen_name in screen_name_list:
            print(user_screen_name)
            try:
                user_id = api.get_user(screen_name=user_screen_name)._json['id_str']
                user_id_list.append(user_id)
            except tweepy.TweepError as e:
                log(4, 'Error while looking for "'+str(user_screen_name)+'" id: '+ str(e.reason) )
        log(1, 'to twitter user_id(s) : '+str(user_id_list))

    #---------------------------------------------------
    # Twitter Streaming
    #---------------------------------------------------

    listener = StdOutListener(
        logger_method= log,
        store_method= store,
        tweet_limit=args.tweets_limit,
        time_limit=args.time_limit
    )
    stream = tweepy.Stream(
        auth,
        listener,
        # tweet_mode = 'extended'
        # { "created_at": ".",..,"retweeted_status": { "extended_tweet": { "full_text":..}..}..}
    )
 
    if (not stream):
        log(5, 'Couldn\'t start stream')
        exit(1)

    # https://github.com/tweepy/tweepy/blob/master/tweepy/streaming.py
    #   def filter(self, follow=None, track=None, async=False,
    #              locations=None, stall_warnings=False, languages=None,
    #              encoding='utf8', filter_level=None)
    # print(args.follow)
    # print(*args.track.split())
    # print(*args.languages.split())

    if len(user_id_list) > 0:
        # https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
        stream.filter(
            follow = [*user_id_list],
            track = [*args.track.split()],
            languages=[args.languages]
        )