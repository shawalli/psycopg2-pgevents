#!/usr/bin/env python
"""
psycopg2-pgevents
-----------------

Adds event notification support for PostGreSQL databases via psycopg2 and
NOTIFY/LISTEN.
"""
from pathlib import Path
from setuptools import setup

about_file = Path(Path(__file__).parent, 'psycopg2_pgevents', '__about__.py')

about = {}
with open(about_file) as f:
    exec(f.read(), about)

long_description = ''
with open('README.rst') as f:
    long_description = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__uri__'],
    license=about['__license__'],
    packages=['psycopg2_pgevents'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'psycopg2-binary>=2.7.5'
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'testfixtures'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
