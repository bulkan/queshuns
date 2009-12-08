from __future__ import with_statement

import redis
import tweetstream



class FilterRedis(object):

    def __init__(self):

        self.key = "tweets"
        self.redis = redis.Redis(host='10')




    def push(self, data):
        self.redis.pus
        




words = ["why", "how", "when"]

with tweetstream.TrackStream("placidified", "ishopsin3021", words) as stream:
    for tweet in stream:
        if '@' in tweet['text'] or not tweet['text'].endswith('?'):
            continue
        print tweet['user']['screen_name'],':', tweet['text'].encode('utf-8')
    
