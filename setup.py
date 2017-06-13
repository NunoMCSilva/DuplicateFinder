#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from dupfinder import __AUTHOR__, __EMAIL__, __VERSION__


def read_file(fname):
    import os
    with open(fname) as f:
        return f.read()


setup(
    name='DuplicateFinder',
    version=__VERSION__,
    description='Find duplicate files',
    #long_description=read_file('README.md'),       # FIXME: FileNotFoundError: [Errno 2] No such file or directory: '/tmp/pip-5esec6ym-build/README.md'
    author=__AUTHOR__,
    author_email=__EMAIL__,
    #FIXME: license=read_file('LICENSE'),
    packages=find_packages(exclude='tests'),
)
