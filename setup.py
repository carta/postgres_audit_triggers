#!/usr/bin/env python
import sys
from distutils.core import setup
from setuptools import find_packages

with open('README.md', 'r') as f:
    long_description = f.read()


if sys.version_info < (3, 5):
    print('Sorry, this module only works on 3.5+')
    sys.exit(1)


setup(name='postgres-audit-triggers',
      version='1.0.0',
      author='Jared Hobbs',
      author_email='jared.hobbs@carta.com',
      license='MIT',
      url='https://github.com/carta/postgres_audit_triggers',
      description='Postgres audit triggers for Django',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(),
      include_package_data=True,
      python_requires='>=3.5',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.5',
          'Topic :: Text Processing',
          'Topic :: Utilities',
      ],
      keywords=['django', 'postgres', 'audit', 'triggers'])
