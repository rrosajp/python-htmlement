from setuptools import setup
from codecs import open as _open
from os import path


def readme():
    # Get the long description from the README file
    readme_file = path.join(path.abspath(path.dirname(__file__)), "README.rst")
    with _open(readme_file, "rb", encoding='utf-8') as opened_file:
        line_sequence = opened_file.readlines()

    # Strips out the seealso directive which is unsupported by pypi and causes problems
    for count, line in enumerate(line_sequence):
        if "seealso::" in line:
            # Strip out this line and the next
            del line_sequence[count]
            del line_sequence[count]
            return "".join(line_sequence)


setup(name='htmlement',
      version='0.2',
      description='Python HTMLParser extension with ElementTree support.',
      long_description=readme(),
      keywords='html html5 parsehtml htmlparser elementtree dom',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Text Processing :: Markup :: HTML',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      url='https://github.com/willforde/python-htmlement',
      platforms=['OS Independent'],
      author='William Forde',
      author_email='willforde@gmail.com',
      license='MIT License',
      py_modules=['htmlement'])
