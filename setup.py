import os
from setuptools import setup, find_packages

__version__ = (0, 1, 0)

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyclimate",
    version='.'.join(str(d) for d in __version__),
    author = "Basil Veerman",
    author_email = "bveerman@uvic.ca",
    description = ("A collection of helpers for processing CMIP5 climate data"),
    url="http://www.pacificclimate.org/",
    packages=find_packages('.'),
    scripts = ['scripts/gen_degree_days.py'],
    install_requires=['netCDF4'],
    long_description=read('README.md')
    )
