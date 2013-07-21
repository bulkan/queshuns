Usage
=====

* Create a Twitter Application at [Twitter Developer](https://dev.twitter.com/apps)
* Create a file `auth.py` and add the variables below and set the values from your new Twitter app

```python
consumer_key        = ""
consumer_secret     = ""
access_token        = ""
access_token_secret = ""
```

More details can be read on the following URL

See http://bulkan-evcimen.com/building_twitter_filter_cherrypy_redis_tweetstream/


queshuns.com
============

This used to run on my old slicehost vps but it was using too much bandwidth. 
Now I've moved it onto a micro EC2 instance and it reads from the streaming api only every 20 seconds.
