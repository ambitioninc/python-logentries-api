# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'logentries_api/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))

requirements = [
    'requests>=2.7.0',
    'six>=1.9.0',
]

import sys
if int(str(sys.version_info.major) + str(sys.version_info.minor)) < 34:
    requirements.append('enum34>=1.0.4')


setup(
    name='python-logentries-api',
    version=get_version(),
    description='A python wrapper for the Logentries API',
    long_description=open('README.rst').read(),
    url='https://github.com/ambitioninc/python-logentries-api',
    author='Micah Hausler',
    author_email='opensource@ambition.com',
    keywords='logs, logentries',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    install_requires=requirements,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=[
        'coverage>=3.7.1',
        'flake8>=2.2.0',
        'mock>=1.3.0',
        'nose>=1.3.0',
    ],
    zip_safe=False,
)
