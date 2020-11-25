
from setuptools import setup, find_packages

NAME = 'bns'

setup(name=NAME,
    version='9999',
    author = "Aurélien Naldi",
    author_email = "aurelien.naldi@gmail.com",
    url = "https://github.com/colomoto/bns-python",
    description = "Python interface to BNS",
    install_requires = [
        "colomoto_jupyter >=0.7.0",
        "pandas",
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords="computational systems biology",

    py_modules = ["bns_setup", "bns"]
)

