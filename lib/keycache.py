"""Client library for using a keycache server.

Example usage.

Default server is "http://keycache.42quarks.com/"

keycache.get(key) returns value or None
keycache.set(key, value) throws Exception on error.

or
kc = keycache.KeyCache(server="http://keycache.42quarks.com/")
kc.get(key)
kc.set(key)

KeyCache pickles and unpickles objects before saving them.
"""

import logging
import json
import urllib
import urllib2
import pickle


class KeyCache():
    def __init__(self,server="http://keycache.42quarks.com/"):
        self.server = server

    def get(self, key):
        res = self.server_rpc('get', params={'key' : key})['payload']
        if res == None:
            return None
        else:
            return pickle.loads(res)
        
    def set(self, key, value):
        self.server_rpc('set', params={'key': key}, payload=pickle.dumps(value))

    def server_rpc(self, hook, params={}, payload=None):
        """GET or POST request to server at URL server/hook with extras dictionary of additional parameters.
        Returns response as a dictionary with JSON response and an entry 'data' if any binary payload is included.

        If payload==None then a POST request is used. Otherwise GET.
        """
        if not payload: # Get request so params are encode in the URL
            hook += '?' + urllib.urlencode(params)
            data = None
        else: # POST request.
            data = json.dumps(params) + '\n\n' + payload
        return self.decode_response(self.server_fetch(hook,data))
            
    def decode_response(self, response):
        """Decode the response (file object) from the server."""
        out = json.loads(response.readline())
        response.readline()
        payload = response.read()
        if len(payload): # Don't save payload if empty
            out['payload'] = payload
        else:
            out['payload'] = None
        return out
            
    def server_fetch(self, hook, data=None):
        url = self.server + hook
        logging.info('Fetching %s' % url)
        return urllib2.urlopen(url, data)
        

defaultkeycache = KeyCache()

get = defaultkeycache.get
set = defaultkeycache.set
