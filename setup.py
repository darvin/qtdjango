#!/usr/bin/env python
import glob
from distutils.core import setup

"""
py2app/py2exe build script for MyApplication.

Will automatically ensure that all build prerequisites are available
via ez_setup

Usage (Mac OS X):
    python setup.py py2app

Usage (Windows):
    python setup.py py2exe

Usage (Ubuntu/Debian):
    python setup.py --command-packages=stdeb.command bdist_deb

Usage (RPM-based linux distros):
    python setup.py bdist_rpm
"""







base_options = dict (name='qtdjango',
      install_requires = ["django", ],
      version='1.1',
      description='''Library for connection of PyQt application to Django server,
also reusable app.''',
      author='Sergey Klimov',
      author_email='dcdarv@gmail.com',
      url='http://github.com/darvin/qtdjango',
      package_dir = {'qtdjango': 'src/qtdjango'},
      packages=['qtdjango',
                'qtdjango.restclient',
                'qtdjango.restclient.httplib2',
                'qtdjango.django_qtdjango'],
      license="GPL",
      maintainer="Sergey Klimov",
      maintainer_email="dcdarv@gmail.com",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
      
     )

options = base_options 



setup( **options)
