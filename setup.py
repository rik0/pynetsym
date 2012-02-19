from os import path
from setuptools import setup, find_packages

version = '0.4.0'

README = path.join(
    path.dirname(__file__),
    'README.rst')
long_description = open(README).read() + "\n\n"

def find_generation_models():
    scripts = glob.glob('pynetsym/generation_models/*.py')
    scripts.pop('pynetsym/generation_models/__init__.py')


setup(
    name='pynetsym', version=version,
    description="Comprehensive package for social networks simulation.",
    long_description=long_description,
    classifiers=[
        "Topic :: Scientific/Engineering :: Mathematics",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="sna sn",
    author="Enrico Franchi",
    author_email="enrico.franchi@gmail.com",
    url="https://github.com/rik0/pynetsym",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'networkx',
        'decorator',
        'numpy',
    ],
)