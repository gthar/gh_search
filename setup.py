#!/usr/bin/env python3

import setuptools


if __name__ == '__main__':
    setuptools.setup(
        name='gh_search',
        version='0.0.1',
        description='Github Search Crawler',
        author='Ricard Illa',
        author_email='r.illa.pujagut@gmail.com',
        packages=['gh_search'],
        py_modules=['gh_search'],
        scripts=['gh_search.py'],
        install_requires=[
            "aiohttp",
            "beautifulsoup4",
            "docopt",
            "requests",
        ],
        test_require=['asynctest'],
        python_requires='>=3.8',
        test_suite="tests",
    )
