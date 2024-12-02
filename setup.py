long_description = """
Python tools

This package contains collection of functions and classes, that are used 
in multiple projects, in order to avoid diverging versions.
"""

from setuptools import setup, find_namespace_packages
from pathlib import Path

# https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
# https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
setup(name='tools',
      version='0.1',
      author='Fabian Scheuermann',
      author_email='fabian.scheuermann@posteo.de',
      license='MIT',
      package_dir={"": "src"},
      packages=find_namespace_packages(where="src"),
      description='Basic tools used in multiple projects',
      long_description = long_description
      )
