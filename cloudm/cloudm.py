"""Library from memoizing python functions (as safely as possible) and saving the results in the cloud."""

import hashlib
import logging
import functools
import pickle
from lib.keycache import KeyCache


class cloudmemoize(object):
   """Decorator that caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned, and
   not re-evaluated.
   """
   def __init__(self, func):
      self.func = func
      self.buildfnhash()
      self.kc = KeyCache('http://keycache.appspot.com/')

   def buildfnhash(self):
       """Build a hash of the function which is hashed to the the argument values so that, as much as possible,
       if the function is modified a new hash is created and so out-of-date values aren't retrieved from the
       cache."""
       h = hashlib.new('sha512')
       h.update('version 1') # If the version is change all hashes will change
       # To a first approximation we just use a hash of the code given by python.
       h.update(str(hash(self.func.func_code)))       
       # TODO in future we'd like to introspection to find what other things depend on this function
       # but this will do for now
       self.fnhash = h.digest()
       
      
   def __call__(self, *args, **xargs):
       # Pickle the arguments check if they're in the cache.
       key = self.hashargs((args, xargs))
       value = self.kc.get(key)
       if value == None: # If the value is empty
           logging.info('Cache miss for %s', self.func.func_name)
           value = self.func(*args)
           self.kc.set(key, value)
       else:
           logging.info('Cache hit for %s', self.func.func_name)
       
       return value

   def hashargs(self, args):
       """Generate a hash from a set of arguments and the fnhash (previously calculated)."""
       h = hashlib.new('sha512')
       h.update(self.fnhash)
       # We use pickle rather than python hash function because it's more reliable and works on
       # most objects.
       h.update(pickle.dumps(args))
       return h.hexdigest()
     
   def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__
   def __get__(self, obj, objtype):
      """Support instance methods."""
      fn = functools.partial(self.__call__, obj)
      return fn

