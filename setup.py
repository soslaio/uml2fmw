# -*- coding: utf-8 -*-
"""Arquivo de instalação do pacote."""

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

requires = [
    'chameleon',
    'lxml',
    'docopt',
]

setup(name='py2fmw',
      version='0.1',
      description='UML to code generator for Python frameworks',
      long_description=README + '\n\n' + CHANGES,
      url='http://github.com/soslaio/py2fmw',
      author='soslaio',
      author_email='soslaio@gentle.com.br',
      license='GNU GPLv3',
      packages=find_packages(),
      include_package_data=True,
      install_requires=requires,
      zip_safe=False)
