import time

import cherrypy
import jinja2
from filter_daemon import *

from simplejson import JSONEncoder
encoder = JSONEncoder()

def jsonify_tool_callback(*args, **kwargs):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    response.body = encoder.iterencode(response.body)

cherrypy.tools.jsonify = cherrypy.Tool('before_finalize', jsonify_tool_callback, priority=30) 

# jinja2 template renderer
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
def render_template(template,**context):
  global env
  template = env.get_template(template+'.jinja')
  return template.render(context)


# QUESHUNS
class Questions(object):
    _cp_config = { 
            'tools.encode.on':True,
            'tools.encode.encoding':'utf8',
            } 
    

    fr = FilterRedis()

    @cherrypy.expose()
    def index(self):
        tweets =  self.fr.tweets(since=0)

        return render_template('index', tweets=tweets)

    @cherrypy.expose()
    def latest(self, since):
        if not since:
            since = 0
        tweets = self.fr.tweets(limit=5, since=float(since))

        return render_template('tweets', tweets=tweets)

#cherrypy.config.update({'server.socket_host': '0.0.0.0',
#                           'server.socket_port': 8085})
cherrypy.quickstart(Questions())
