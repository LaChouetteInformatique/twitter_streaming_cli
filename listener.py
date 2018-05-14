import tweepy # Twitter mining/streaming lib
import time
import json


class StdOutListener(tweepy.streaming.StreamListener):
    ''' Handles data received from twitter API stream.
    '''
    # kind = 'canine'    # class variable shared by all instances
    
    def __init__(
        self,
        logger_method=print,
        store_method=None,
        tweet_limit=0,
        time_limit=0
    ):
        # Call initial constructor of StdOutListener
        super(StdOutListener, self).__init__()

        self.start_time = time.time()
        # Where to limit time?
        # How to properly close stream?
        self.time_limit = time_limit

        self.timeout_counter = 0

        # Streamed Tweets counter
        self.tweets_count = 0

        # Max number of tweets to collect
        self.tweet_limit = tweet_limit

        self.log = logger_method
        #self.log('info','Listener initialised')
        self.store = store_method

    def keep_alive(self):
        """ https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/connecting
        The Streaming API will send a keep-alive newline every 30 seconds
        to prevent your application from timing out the connection.
        So that's a good spot to check elapsed time since self.start_time """
        return self.check_listener_ttl()

    def check_listener_ttl(self):
        """ Return False if Time to stop is reached
            time_limit = 0 => no time limit (alwais return True)
        """
        if (self.time_limit == 0):
            return True
        if (time.time() - self.start_time) < self.time_limit:
            return True # Keep streaming
        else:
            self.log('debug','check_listener_ttl: time_limit reached')
            return False
    
    def tweets_counter(self):
        """ Count collected tweets and return false if tweet_limit is reached
            tweet_limit == 0: means no limit """

        if self.tweet_limit == 0:
            return True

        self.tweets_count += 1

        if self.tweet_limit > 0:
            if self.tweets_count < self.tweet_limit:
                return True
            else:
                self.log('debug','tweets_counter: tweet_limit reached' )
                return False

    def on_status(self, status):
        """ What happen when stream got new tweet
        After each new tweet, we check for tweet_limit and time_limit

        NOTE : api.rate_limit_status['remaining_hits'] as a gauge,
            and then use sleep() for the remaining time left until the API
            limit resets whenever you're about to run out of calls
        """

        print('Tweet text: ' + status.text)
        if (self.store != None):
            self.store(status._json)

        # There are many options in the status object,
        # hashtags can be very easily accessed.
        #for hashtag in status.entries['hashtags']:
        #    print(hashtag['text'])

        #text = status.text
        #created = status.created_at
        #record = {'Text': text, 'Created At': created}
        #print record #See Tweepy documentation to learn how to access other fields
        #collection.insert(record)

        if (self.tweets_counter() and self.check_listener_ttl() ):
            return True # continue streaming
        else:
            self.log('debug','on_status: Stopping Streaming' )
            return False


    def on_timeout(self):
        """ Timeout management
            more than 3 timeout => stop stream
        """
        self.timeout_counter += 1
        if (self.timeout_counter > 3):
            self.log('debug','on_timeout: Stream disconnected, timeout_counter={}, stopping stream'
                .format(self.timeout_counter))
            return False
        else:
            self.log('debug','on_timeout: Stream disconnected, timeout_counter={}, continuing...'
                .format(self.timeout_counter))
            return True # continue listening
 
    
    def on_error(self, status_code):
        """ Handling of errors
        TODO: get time to wait before reconnection and auto-reconnect.
        TODO: eventually, use search API to get missed tweets while disconnected
        see http://docs.tweepy.org/en/v3.6.0/streaming_how_to.html#handling-errors
        most important error seem to be 420:
        see https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/connecting
            Back off exponentially for HTTP 420 errors.
            Start with a 1 minute wait and double each attempt.
            Note that every HTTP 420 received increases the time you must wait until
            rate limiting will no longer will be in effect for your account
        """
        self.log('error','Got an error with status code: {}'.format(str(status_code)))
        #https://developer.twitter.com/en/docs/basics/response-codes
        if (status_code == 420):
            # TODO Set timer instead of leaving
            self.log(4,'application is being rate limited for making too many requests')
            # TODO Set timer instead of leaving
            return False
        elif (status_code == 429):
            self.log(4,'request cannot be served due to the application’s rate'
            +'limit having been exhausted for the resource. ')
            # TODO Set timer instead of leaving
            return False
        elif (status_code == 406):
            self.log(5,'Invalid format is specified in the request, exiting')
            return False
        else:
            return True # continue listening


    if __name__ == '__main__':
        print("hello")