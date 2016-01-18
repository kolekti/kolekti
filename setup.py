from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='kolekti',
    version='0.1',
    description='a technical documentation publication engine',
    long_description=long_description,
    url='https://github.com/kolekti/kolekti',
    author='Stephane Bonhomme',
    author_email='stephane@exselt.com',
    license='AGPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Documentation',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='documentation docs publishing system',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    py_modules=['kolekti_run'],
    include_package_data=True,
    install_requires=['lxml', 'whoosh'],
    entry_points={
        'console_scripts': [
            'kolekti=kolekti_run:main',
        ],
    },
)
