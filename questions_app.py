import time
import os

import cherrypy
import jinja2
from filter_daemon import *

try:
    import json
except:
    import simplejson as json

from simplejson import JSONEncoder
encoder = JSONEncoder()

def jsonify_tool_callback(*args, **kwargs):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    response.body = encoder.iterencode(response.body)

cherrypy.tools.jsonify = cherrypy.Tool('before_finalize', jsonify_tool_callback, priority=30) 

root_path = os.path.dirname(__file__)


# jinja2 template renderer
env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(root_path, 'templates')))
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
    @cherrypy.tools.jsonify()
    def latest(self, since, nt):
        #cherrypy.response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate';
        #cherrypy.response.headers['Cache-Control'] = 'post-check=0, pre-check=0';
        #cherrypy.response.headers['Pragma'] = 'no-cache';

        cherrypy.response.headers['Expires'] = 'Sun, 19 Nov 1978 05:00:00 GMT'
        cherrypy.response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        cherrypy.response.headers['Pragma'] = 'no-cache'
        #cherrypy.response.headers['Content-Type'] = "application/json"


        if not since:
            since = 0
        tweets = self.fr.tweets(limit=5, since=float(since))

        return render_template('tweets', tweets=tweets)

def setup_server():
    # Set up site-wide config. Do this first so that,
    # if something goes wrong, we get a log.
    cherrypy.config.update({'environment': 'production',
                    'log.screen': False,
                    'show_tracebacks': False,
                    'log.error_file': '/tmp/site.log',
                    })

    cherrypy.tree.mount(Questions())




if __name__ == '__main__':
    setup_server()
    #cherrypy.config.update({'server.socket_host': '0.0.0.0',
    #                           'server.socket_port': 8085})

    #engine = cherrypy.engine
    #from cherrypy.process import plugins, servers
    #cherrypy.config.update({'log.screen': False})
    #plugins.Daemonizer(engine).subscribe()

    #engine.start()
    #cherrypy.quickstart(Questions())
