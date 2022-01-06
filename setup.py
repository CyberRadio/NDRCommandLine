from setuptools import find_packages
from distutils.core import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os
import pwd

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        path = '/home/ndruser/Desktop/NDR562_Releases/'
        isFile = os.path.isdir(path)
        if isFile == False:
            try:
                os.mkdir(path)
            except OSError:
                print ("Creation of the directory %s failed" % path)
            else:
                print ("Successfully created the directory %s " % path)

VERSION='20.03.12'

DATA_FILES = [('/usr/share/applications/',['NDR562CommandLine.Desktop'])]
SCRIPTS = ['ndrcommandline.py']

setup(name='NDRXXXCommandLine',
      version=VERSION,
      packages=None,
      data_files=DATA_FILES,
      scripts=SCRIPTS
      )
