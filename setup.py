# coding: utf-8

from setuptools import setup, find_packages

NAME = "vw-webapp"
VERSION = "1.0.0"


# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "flask>=0.10.0",
    "flask-cors>=2.1.0",
    "flask-script>=2.0.5",
    "flask-migrate>=1.3.0",
    "flask-moment>=0.4.0",
    "flask-sqlalchemy>=2.1",
    "flask-wtf>=0.11",
    "flask-login>=0.2.11",
    "vw-gstore-adapter==1.0.0"
]

setup(
    name=NAME,
    version=VERSION,
    description="Virtual Watershed web app for navigation, modeling, and data management",
    author="Matthew A. Turner",
    author_email="maturner01@gmail.com",
    url="https://virtualwatershed.org",
    keywords=["REST", "Hydrology"],
    install_requires=REQUIRES,
    # dependency_links=DEPENDENCY_LINKS,
    packages=find_packages(),
    include_package_data=True,
    license='BSD3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7'
    ]
)
