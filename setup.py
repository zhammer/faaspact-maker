"""Setup for pytest-hammertime plugin."""

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

from setuptools import find_packages, setup

pipfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pipfile['packages'], r=False)

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='faaspact-maker',
    version='0.0.10',
    description='Make and mock pacts in python for faas microservices.',
    url='https://github.com/zhammer/faaspact-maker',
    packages=find_packages(),
    install_requires=requirements,
    author='Zach Hammer',
    author_email='zach.the.hammer@gmail.com',
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
