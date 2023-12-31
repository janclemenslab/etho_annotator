from setuptools import setup, find_packages
import os
import codecs
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='etho annotator',
    version=find_version("src/etho_annotator/__init__.py"),
    description='etho_annotator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/janclemenslab/etho_annotator',
    author='Jan Clemens',
    author_email='clemensjan@googlemail.com',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    # install_requires=['numpy', 'pyvideoreader', 'pyqqtgraph', 'qtpy'],
    include_package_data=True,
    zip_safe=False
    )
