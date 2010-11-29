'''
DataDiff
========

DataDiff is a library to provide human-readable diffs of python data structures.
It can handle sequence types (lists, tuples, etc), sets, and dictionaries.

It has special-case handling for multi-line strings, showing them as a typical unified diff.
Lists will be diffed recursively, when applicable.

``datadiff`` works on Python 2.5 through Python 3.

DataDiff project homepage: http://sourceforge.net/projects/datadiff/

Example
-------

Here's an example::

    >>> from datadiff import diff
    >>> a = [2, 3, 4, 5, 6]
    >>> b = [2, 3, 4, 6]
    >>> print diff(a, b)
    --- a
    +++ b
    [
    @@ -0,4 +0,3 @@
     2,
     3,
     4,
    -5,
     6,
    ]
    >>>

License
-------

Copyright 2010 Dave Brondsema

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

'''

from distutils.core import setup
import setuptools # for extra commands
setup(
    name = 'datadiff',
    packages = ['datadiff'],
    version = '1.0.0',
    description = 'DataDiff is a library to provide human-readable diffs of python data structures.',
    long_description = __doc__,
    author = 'Dave Brondsema',
    author_email = 'dave@brondsema.net',
    url = 'http://sourceforge.net/projects/datadiff/',
    keywords = ['data', 'diff'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license = 'Apache License',
)
