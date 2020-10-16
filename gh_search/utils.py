"""
Misc helpers
"""


import json
import logging
import os
import random
import re
import sys

from gh_search.fetchers import fetch_links, fetch_lang_stats


logger = logging.getLogger(__name__)


def get_owner(link):
    """
    Get the owner of a given github repo link
    """
    pattern = r'^(http(s)?://)?(www\.)?github\.com/+([^\/]+)/+.+$'
    return re.search(pattern, link).group(4)


def set_proxy(proxies, verbose=False):
    proxy = random.choice(proxies)
    os.environ['HTTP_PROXY'] = proxy
    logging.getLogger(__name__).info(f'proxy set to `{proxy}`')


def read_input(infile):
    logger.info('input file: `{infile`}')
    with open(infile, 'r') as fh:
        try:
            input_data = json.load(fh)
        except json.JSONDecodeError:
            logger.error('badly formatted json')
            sys.exit(1)

    try:
        keywords = input_data['keywords']
        proxies = input_data['proxies']
        page_type = input_data['type']
    except KeyError:
        logger.error('missing needed key in input file')
        sys.exit(1)

    keywords = list(map(str, keywords))
    proxies = list(map(str, proxies))
    page_type = str(page_type).lower()

    if page_type not in ('repositories', 'issues', 'wikis'):
        logger.error('invalid type: `{page_type}`')
        sys.exit(1)

    return keywords, proxies, page_type


def write_output(result, outfile=None):
    if outfile:
        logger.info('writing to file: `{outfile}`')
        with open(outfile, 'w') as fh:
            json.dump(result, fh, indent=2)
    else:
        logger.info('writing to standard output')
        sys.stdout.write(json.dumps(result, indent=2))


def gh_search(keywords, page_type, gh_url):
    links = fetch_links(keywords, page_type, gh_url)
    if page_type == "repositories":
        return [
            {
                'url': link,
                'extra': {
                    'owner': get_owner(link),
                    'language_stats': stats
                }
            }
            for link, stats in zip(links, fetch_lang_stats(links))]
    else:
        return [{'url': link} for link in links]
