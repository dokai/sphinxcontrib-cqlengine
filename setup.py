# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
Sphinx directive to generate automatic Cassandra CQL table documentation and
diagrams for cqlengine models.
'''

requires = [
    'Sphinx>=0.6',
    'sphinxcontrib-blockdiag',
]

setup(
    name='sphinxcontrib-cqlengine',
    version='0.2',
    url='https://github.com/dokai/sphinxcontrib-cqlengine',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-cqlengine',
    license='BSD',
    author='Kai Lautaportti',
    author_email='kai.lautaportti@gmail.com',
    description='Sphinx "cqlengine" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
