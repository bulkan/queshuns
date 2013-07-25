import time
import json

import redis
from twython import TwythonStreamer

from auth import consumer_key, consumer_secret, access_token_secret, access_token


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


class StreamWatcherListener(TwythonStreamer):
    fr = FilterRedis()

    tweet_count = 0

    def on_success(self, data):
        tweet = data
        if not 'text' in tweet:
            return
        try:
            if '@' in tweet['text'] or not tweet['text'].endswith('?'):
                return True
            print tweet['text'].encode('utf-8')
            print '\n %s  %s\n' % (tweet['user']['screen_name'], tweet['created_at'])

            self.fr.push(json.dumps( {
                'id': tweet['id'],
                'text': tweet['text'],
                'username': tweet['user']['screen_name'],
                'userid': tweet['user']['id'],
                'name': tweet['user']['name'],
                'profile_image_url': tweet['user']['profile_image_url'],
                'received_at': time.time()
            }))
            self.tweet_count += 1
            if self.tweet_count >= 10:
                print 'got 10 tweets sleeping'
                time.sleep(25)
                self.tweet_count = 0
        except Exception, e:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            print e

    def on_error(self, status_code, data):
        print 'An error has occured! Status code = %s' % status_code
        time.sleep(20)

    def on_timeout(self):
        print 'Snoozing Zzzzzz'
        time.sleep(10)


if __name__ == '__main__':
    words = ["why", "how", "when", "where", "who", "feeling", "lol"]

    #auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    #auth.set_access_token(access_token, access_token_secret)

    #stream = tweepy.Stream(auth, StreamWatcherListener(), timeout=None)
    #stream.filter(None, words)

    stream = StreamWatcherListener(consumer_key, consumer_secret, access_token, access_token_secret)
    stream.statuses.filter(track=words)
