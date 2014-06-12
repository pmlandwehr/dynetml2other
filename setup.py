#!/usr/bin/env python

__author__ = 'plandweh'


from distutils.core import setup

setup(name='dynetml2other',
      version='0.1',
      description='DyNetML parsing and manipulation',
      long_description=open('README.md').read(),
      author='Peter Landwehr',
      author_email='plandweh@cs.cmu.edu',
      url='http://pmlandwehr.github.com/dynetml2other',
      requires=['lxml'],
      packages=['dynetml2other']
     )