#!/usr/bin/env python

from distutils.core import setup

setup(name='cloudm',
      version='0.1.6',
      packages = ['cloudm', 'cloudm.tests'],  # include all packages under src
      author="Jonathan Hunt", author_email="jjh@42quarks.com",
      description="Library for easy memoization using Google App Engine memcache.",
      license="MIT",
      url="https://github.com/jjh2/cloudm")
