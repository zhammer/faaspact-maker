"""Setup for pytest-hammertime plugin."""

from setuptools import setup

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

pipfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pipfile['packages'], r=False)

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='faaspact-maker',
    version='0.0.7',
    description='Make and mock pacts in python for faas microservices.',
    url='https://github.com/zhammer/faaspact-maker',
    packages=('faaspact_maker',),
    install_requires=requirements,
    author='Zach Hammer',
    author_email='zach.the.hammer@gmail.com',
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
