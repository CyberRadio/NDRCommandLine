#!/usr/bin/env python3

# Imports
import os
from datetime import datetime
import fnmatch
from setuptools import setup, find_packages

_VERSION = "25.02.11"

def get_folder_paths_recursive(install_dir, base_dir):
    ret = []
    files = []
    target_folder = base_dir.split('/')[-2]
    _install_dir = "%s%s/"%(install_dir, target_folder)
    
    for item in os.listdir(base_dir):
        file_or_dir = "%s%s"%(base_dir, item)
        if os.path.isdir(file_or_dir):
            dir = "%s%s/"%(base_dir, item)
            print(dir)
            ret.extend(get_folder_paths_recursive(_install_dir, dir))
        else:
            files.append(file_or_dir)
    ret.append((_install_dir, files))
    return ret


def get_all_files(install_dir, base_dir):
    ret = []
    files = []
    for item in os.listdir(base_dir):
        file_or_dir = "%s%s"%(base_dir, item)
        if not os.path.isdir(file_or_dir):
            file = "%s%s"%(base_dir, item)
            files.append(file)
    ret.append((install_dir, files))
    return ret

def get_executable_files(install_dir, base_dir, file_type):
    ret = []
    files = []
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, '*{0}'.format(file_type)):
            files.append(os.path.join(root, filename))
    ret.append((install_dir, files))
    return ret


# Get package version from date
now = datetime.now()
VERSION = now.strftime("%y.%m.%d")
DATA_FILES = []
PACKAGES = [] # find_packages()

# AUTHOR: Author of the application
AUTHOR='Brandon Smith'

# EMAIL: E-mail address for the maintainer of the application
EMAIL='brandon.smith@g3ti.net'

# PACKAGE_LIST: List of Python packages to install
PACKAGE_LIST = []

# SCRIPT_LIST: List of script files to install to /usr/bin/.
SCRIPT_LIST = ['scripts/ndrxxx_command_line.py']

# DATA_FILE_LIST: Data file information.  This is a list of 2-tuples: (install directory, list of data files).
DATA_FILE_LIST = [('/usr/share/applications/', ['shortcuts/CRS-NDRCommandLineNDR358.desktop', 'shortcuts/CRS-NDRCommandLineNDR551.desktop', 'shortcuts/CRS-NDRCommandLineNDR562.desktop'])]

setup (
    name='ndrcommandline', 
    version=_VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description="NDRxxx Commandline Utility for sending JSON Messages",
    url="https://gitlab.mamd.g3ti.local/RadioCode/ndrcommandline",
    scripts=SCRIPT_LIST,
    packages=PACKAGES,
    data_files=DATA_FILE_LIST,
)

