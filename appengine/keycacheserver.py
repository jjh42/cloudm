"""Provides a very thin wrapper around memcache for remote calls.

We encode results (and applications must encode sets) in the following way.

1 line of JSON ended by a newline
blank line
binary file (no encoding applied)

The JSON field should contain a 'key' value. A result will contain a 'key' value and either a hit or a miss.

Procedures provided are:
get returns a JSON result {'key': keyvalue, hit: True or False} followed by newline followed by the key.
set expects a JSON {'key': keyvalue } followed by a newline followed by the data to cache.
"""

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
import os
import logging
import hashlib


class GetHandler(webapp.RequestHandler):
    def get(self):
        key = self.request.get('key')
        logging.info('Cache request for key: %s' % key)
        value = memcache.get(key)
        hit = value != None
        self.response.out.write(json.dumps({'key': key, 'hit' : hit}))
        self.response.out.write('\n\n')
        if hit:
            logging.info('Cache hit')
            self.response.headers.add_header('Cache-Control', 'public, max-age=86400')
            self.response.out.write(value)
        else:
            # Cache miss
            self.response.headers.add_header('Cache-Control', 'no-cache')
            logging.info('Cache miss')
    
class SetHandler(webapp.RequestHandler):
    def post(self):
        key = json.loads(self.request.body_file.readline())['key']
        self.request.body_file.readline() # Skip blank line
        value = self.request.body_file.read()
        memcache.set(key, value)
        self.response.out.write(json.dumps({'key' : key, 'cached' : True,
                                           'value_sha512' : hashlib.sha512(value).hexdigest()}))
        self.response.out.write('\n\n')

application = webapp.WSGIApplication([('/get', GetHandler), ('/set', SetHandler)],
                                     debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
