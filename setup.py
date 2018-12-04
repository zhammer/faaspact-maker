"""Setup for pytest-hammertime plugin."""

from setuptools import setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='faaspact-maker',
    version='0.0.6',
    description='Make and mock pacts in python for faas microservices.',
    url='https://github.com/zhammer/faaspact-maker',
    packages=('faaspact_maker',),
    author='Zach Hammer',
    author_email='zach.the.hammer@gmail.com',
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
