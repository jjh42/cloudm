import unittest
from google.appengine.api import memcache
import keycacheserver
import lib.keycache as kc
from gaetestbed import UnitTestCase, FunctionalTestCase
import json
from StringIO import StringIO
import logging

class InternalKeyCache(kc.KeyCache):
    def __init__(self, app):
        self.app = app
        
    def server_fetch(self, hook, data):
        # Override for testing purposes to directly call the handler."""
        if not data: # Get request
            res =  self.app.get('/' + hook)
        else:
            res = self.app.post('/' + hook,data)
        logging.info('Server response:\n' + str(res))
        return StringIO(res.body)

class TestKeyStore(FunctionalTestCase, unittest.TestCase):
    APPLICATION = keycacheserver.application
    def setUp(self):
        super(TestKeyStore, self).setUp()
        self.kcclient = InternalKeyCache(self)

    def test_cachemiss(self):
        """Test uploading a small blob."""
        self.assertEqual(self.kcclient.get('cachemiss'), None)

    def test_cachehit(self):
        """Test hit and retrieve a blob."""
        self.kcclient.set('cachehit', 'value')
        self.assertEqual(self.kcclient.get('cachehit'), 'value')

