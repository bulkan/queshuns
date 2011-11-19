import time

import redis
import tweepy

import json

from auth import username, password


class FilterRedis(object):

    key = "tweets"
    r = redis.Redis(host='localhost', port=6379)
    num_tweets = 20
    trim_threshold = 100

    def __init__(self):
        self.trim_count = 0


    def push(self, data):
        self.r.lpush(self.key, data)

        self.trim_count += 1
        if self.trim_count >= self.trim_threshold:
            self.r.ltrim(self.key, 0, self.num_tweets)
            self.trim_count = 0


    def tweets(self, limit=15, since=0):
        data = self.r.lrange(self.key, 0, limit - 1)
        return [json.loads(x) for x in data if int(json.loads(x)['received_at']) > since]


class StreamWatcherListener(tweepy.StreamListener):
    fr = FilterRedis()

    def on_status(self, status):
        tweet = status
        try:
            if '@' in tweet.text or not tweet.text.endswith('?'):
                return True
            print  tweet.text.encode('utf-8')
            print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
            self.fr.push(json.dumps( {'id':tweet.id,
                                 'text':tweet.text,
                                 'username':tweet.author.screen_name,
                                 'userid':tweet.author.id,
                                 'name':tweet.author.name,
                                 'profile_image_url':tweet.author.profile_image_url,
                                 'received_at':time.time()
                                 } 
                               )
                    )
        except:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            pass

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keep stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'


if __name__ == '__main__':
    #fr = FilterRedis()

    words = ["why", "how", "when", "where", "who", "feeling", "lol"]
    
    auth = tweepy.auth.BasicAuthHandler(username, password)

    stream = tweepy.Stream(auth, StreamWatcherListener(), timeout=None)
    stream.filter(None, words)

    #with tweetstream.TrackStream("placidified", "ishopsin3021", words) as stream:
    #    for tweet in stream:
    #        if 'text' not in tweet: continue
    #        if '@' in tweet['text'] or not tweet['text'].endswith('?'):
    #            continue
    #        fr.push(json.dumps( {'id':tweet['id'],
    #                             'text':tweet['text'],
    #                             'username':tweet['user']['screen_name'],
    #                             'userid':tweet['user']['id'],
    #                             'name':tweet['user']['name'],
    #                             'profile_image_url':tweet['user']['profile_image_url'],
    #                             'received_at':time.time()}
    #                             )
    #                )
    #        print tweet['user']['screen_name'],':', tweet['text'].encode('utf-8')
