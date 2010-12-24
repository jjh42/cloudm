"""Library from memoizing python functions (as safely as possible) and saving the results in the cloud."""

import hashlib
import logging
import functools
from functools import partial
import itertools
import pickle
from decorator import decorator, FunctionMaker
from keycache import KeyCache
from collections import defaultdict
from Queue import Queue
from threading import Thread, Lock

class BaseClassMemoize(object):
   """Base class for memoizing a function using a list of dictionaries.

   It will check the dictionaries in order for a cache function evaluation and avoid
   function evaluation if run. 
   """
   # See below for how to use this class.

   # Dictionary that controls caching.
   cachecontrol = {'writeonly' : False }

   extrahash = 'FOOBAR' # Extra hash to can be modified to generate cache misses if needed.
   
   def __init__(self, func, caches):
      """Use partial to build a constructor that provides some dictionaries in caches for caching."""
      self.func = func
      self.caches = caches
      self.buildfnhash()
      functools.update_wrapper(self, func)

   def buildfnhash(self):
       """Build a hash of the function which is hashed to the the argument values so that, as much as possible,
       if the function is modified a new hash is created and so out-of-date values aren't retrieved from the
       cache."""
       h = hashlib.new('sha512')
       h.update('version 1') # If the version is change all hashes will change
       # To a first approximation we just use a hash of the code given by python.
       func_code = self.func.func_code
       # In case another 
       h.update(str(hash(self.func.func_code)))
       h.update(self.func.func_code.co_filename)
       h.update(self.func.func_code.co_code)
       # TODO in future we'd like to introspection to find what other things depend on this function
       # but this will do for now
       self.fnhash = h.digest()

   def __call__(self, *args, **xargs):
       # Pickle the arguments check if they're in the cache.
       key = self.hashargs((args, xargs))

       cacheindex = len(self.caches)
       if not self.cachecontrol['writeonly']: # Write to the cache.
          for d,i in zip(self.caches, range(len(self.caches))): # Find the first cache to have a hit.
             value = d[key]
             if value != None:
                cacheindex = i
                cachetype = type(d)
                break
       else:
          value = None
          
       if value == None: # If the value is empty
           logging.info('Cache miss for %s', self.func.func_name)
           value = self.func(*args, **xargs)
       else:
           logging.info('Cache hit (type %s) for %s', str(cachetype), self.func.func_name)

       # Update any caches further up with the key.
       for d in self.caches[0:cacheindex]: 
              d[key] = value
       
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


def decorator_apply(dec, func):
    """
    Decorate a function by preserving the signature even if dec
    is not a signature-preserving decorator.
    """
    return FunctionMaker.create(
        func, 'return decorated(%(signature)s)',
        dict(decorated=dec(func)), undecorated=func)



class ThreadWriteKeyCache(KeyCache):
   """Wrapper around KeyCache so that writes are threaded and don't delay other code."""      
   def set(self,key,value):
      logging.info('Setting %s to %s in thread.' % (str(key), str(value)))
      t = Thread(target=partial(KeyCache.set, self, key, value))
      t.start()


kc = ThreadWriteKeyCache('http://keycache.appspot.com/')


def cloudmemoize(func):
    """Decorator for memoizing a function using a memory based cache and a Google App Engine based cache."""
    return decorator_apply(partial(BaseClassMemoize, caches=[defaultdict(itertools.repeat(None).next), kc]), func)

def memmemoize(func):
   """Decorator for memoizing a function using on a memory based cache."""
   return decorator_apply(partial(BaseClassMemoize, caches=[defaultdict(itertools.repeat(None).next)]), func)

