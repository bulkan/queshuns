from __future__ import with_statement

from datetime import datetime

import time

import redis
import tweetstream

try:
    import simplejson as json
except:
    import json


class FilterRedis(object):

    key = "tweets"
    r = redis.Redis(host='bulkan-evcimen.com')
    r.connect()
    num_tweets = 20
    trim_threshold = 100

    def __init__(self):
        self.trim_count = 0


    def push(self, data):
        self.r.push(self.key, data, True)

        self.trim_count += 1
        if self.trim_count >= self.trim_threshold:
            self.r.ltrim(self.key, 0, self.num_tweets)
            self.trim_count = 0

    def tweets(self, limit=15, since=0):
        data = self.r.lrange(self.key, 0, limit - 1)
        return [json.loads(x) for x in data if int(json.loads(x)['received_at']) > since]


if __name__ == '__main__':
    fr = FilterRedis()

    words = ["why", "how", "when", "lol", "feeling"]

    with tweetstream.TrackStream("placidified", "ishopsin3021", words) as stream:
        for tweet in stream:
            if 'text' not in tweet: continue
            if '@' in tweet['text'] or not tweet['text'].endswith('?'):
                continue
            fr.push(json.dumps( {'id':tweet['id'],
                                 'text':tweet['text'],
                                 'username':tweet['user']['screen_name'],
                                 'userid':tweet['user']['id'],
                                 'name':tweet['user']['name'],
                                 'profile_image_url':tweet['user']['profile_image_url'],
                                 'received_at':time.time()}
                                 )
                    )
            print tweet['user']['screen_name'],':', tweet['text'].encode('utf-8')
