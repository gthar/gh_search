#!/usr/bin/env python3

"""
Github Search Crawler

Usage:
    gh_search.py INPUT_FILE [--output=OUT_FILE | -o OUT_FILE] [--verbose | --quiet]
    gh_search.py (-h | --help)
    gh_search.py --version

Options:
    -h --help                      show this screen.
    -o OUT_FILE --output=OUT_FILE  specify the output file (by default, stdout)
    --verbose                      print more logging info
    --quiet                        print less logging info
"""  # noqa


import logging
import sys

from docopt import docopt

from gh_search.utils import set_proxy, read_input, write_output, gh_search


VERSION = '0.0.1'
NAME = 'Github Search Crawler'

GH_URL = 'https://github.com'


def main():
    arguments = docopt(__doc__, version=f'{NAME} {VERSION}')

    logging.basicConfig()
    if arguments['--verbose']:
        logging.getLogger().setLevel(logging.INFO)
    elif arguments['--quiet']:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    infile = arguments['INPUT_FILE']
    keywords, proxies, page_type = read_input(infile)

    set_proxy(proxies)
    result = gh_search(keywords, page_type, GH_URL)

    write_output(result, arguments['--output'])

    return 0


if __name__ == '__main__':
    sys.exit(main())
