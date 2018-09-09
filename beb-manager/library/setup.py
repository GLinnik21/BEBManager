from setuptools import setup, find_packages

setup(
    name='beb_lib',
    version='0.0.1',
    description='Simple library for issues tracking',
    author='Gleb Linnik',
    author_email='gleb_linnik@icloud.com',
    url='https://bitbucket.org/GLinnik/isp',
    install_requires=['peewee'],
    packages=find_packages(exclude='tests'),
    test_suite='tests.run_tests'
)
