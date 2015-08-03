#!/usr/bin/env python

from distutils.core import setup

setup(name='betadataservices',
      version='0.1.0',
      install_requires=["requests >= 2.3.0",
                        "python-dateutil"],
      description='Python interface to beta data services',
      author='Met Office Informatics Lab',
      maintainer='Met Office Informatics Lab',
      url='https://github.com/met-office-lab/beta-data-services',
      license='TBC',
      packages=['betadataservices'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ]
     )
