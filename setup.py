from setuptools import setup
from codecs import open
from os import path
import re

# Path to local directory
here = path.abspath(path.dirname(__file__))


def readfile(filename):  # type: (str) -> str
    """Get the long description from the README file"""
    readme_file = path.join(here, filename)
    with open(readme_file, "r", encoding="utf-8") as stream:
        return stream.read()


def extract_variable(filename, variable):  # type: (str, str) -> str
    """Extract the version number from a python file that contains the '__version__' variable."""
    with open(filename, "r", encoding="utf8") as stream:
        search_refind = r'{} = ["\'](\d+\.\d+\.\d+)["\']'.format(variable)
        verdata = re.search(search_refind, stream.read())
        if verdata:
            return verdata.group(1)
        else:
            raise RuntimeError("Unable to extract version number")


setup(
    name='htmlement',
    version=extract_variable('htmlement.py', '__version__'),
    description='Pure-Python HTML parser with ElementTree support.',
    long_description=readfile('README.rst'),
    extras_require={"dev": ["pytest", "pytest-cov"]},
    keywords='html html5 parsehtml htmlparser elementtree dom',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    url='https://github.com/willforde/python-htmlement',
    platforms=['OS Independent'],
    author='William Forde',
    author_email='willforde@gmail.com',
    license='MIT License',
    py_modules=['htmlement']
)
