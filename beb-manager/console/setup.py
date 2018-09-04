from setuptools import setup, find_packages

setup(
    name='beb-manager',
    version='0.0.1',
    description="Simple CLI task tracker",
    author="Gleb Linnik",
    author_email="gleb_linnik@icloud.com",
    url='https://bitbucket.org/GLinnik/isp',
    install_requires=['peewee', 'beb_lib'],
    packages=find_packages(),
    entry_points='''
    [console_scripts]
    beb-manager=beb_manager_cli.application.main:main'''
)
