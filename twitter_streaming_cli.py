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

    parser.add_argument("--txt",
        action="store_true",
        help="Generate a TXT file with tweet's text content. JSON one will still be generated"
    )

    args = parser.parse_args()

    log = super_logger(
        txt_output = True,
        log_lvl = args.loglvl
        )


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
    # Twitter Streaming
    #---------------------------------------------------

    listener = StdOutListener(
        logger_method= log,
        tweet_limit=args.tweets_limit,
        time_limit=args.time_limit
    )
    stream = tweepy.Stream(auth, listener)
 
    if (not stream):
        log(5, 'Couldn\'t start stream')
        exit(1)

    # https://github.com/tweepy/tweepy/blob/master/tweepy/streaming.py
    #   def filter(self, follow=None, track=None, async=False,
    #              locations=None, stall_warnings=False, languages=None,
    #              encoding='utf8', filter_level=None)
    stream.filter(
        follow=[args.follow],
        track = [args.track],
        languages=[args.languages]
    )

