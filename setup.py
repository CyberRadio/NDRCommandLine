from setuptools import find_packages
from distutils.core import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os
import pwd

VERSION='20.03.12'

SCRIPTS = ['ndrcommandline.py']

setup(name='NDRXXXCommandLine',
      version=VERSION,
      packages=None,
      scripts=SCRIPTS
      )
