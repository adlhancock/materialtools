# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

"""
# Need to clarify which license, given UKAEA and UoS responsibilities
with open('LICENSE') as f:
    license = f.read()
"""

setup(
    name='materialtools',
    # version='0.0.1',
    description='Tools for manipulating material property data',
    long_description=readme,
    author='David Hancock',
    author_email='david@adlhancock.net',
    url='https://github.com/adlhancock/materialtools',
    #license=license,
    packages=find_packages(exclude=('tests', 'docs','sampledata'))
)