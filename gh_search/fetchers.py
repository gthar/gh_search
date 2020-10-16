"""
Functions that fetch data using http requests
"""

import asyncio
import logging
import os
import random
import sys
import time

import aiohttp
import requests

from gh_search.parse_html import parse_links, parse_repo_lang_stats


MAX_BACKOFF = 64
MAX_TRIES = 10

logger = logging.getLogger(__name__)


def _backoff_wait_time(i):
    """
    Calculate the backoff wait time
    """
    return min(2**i + random.random(), MAX_BACKOFF)


def fetch_links(keywords, page_type, gh_url):
    """
    Given a list of keywords and a type to search, return a list of links
    Using truncated exponential backoff as explained here:
    https://cloud.google.com/storage/docs/exponential-backoff
    """
    search_url = f'{gh_url}/search'
    proxy = os.environ['HTTP_PROXY']

    for i in range(MAX_TRIES):

        logger.info(f'fetching data from `{search_url}` using proxy `{proxy}`')
        response = requests.get(
            search_url,
            params={
                'q': '+'.join(keywords),
                'type': page_type})

        status = response.status_code

        if status == 429 or str(status).startswith('5'):
            # exponential backoff
            wait_time = _backoff_wait_time(i)
            logger.warning(f'waiting `{wait_time}` before trying again')
            time.sleep(wait_time)

        elif status == 200:
            content = response.content.decode('utf-8')
            links = parse_links(content, page_type, gh_url)
            return links

        else:  # I consider any other status code as an error
            break

    logger.error(f'could not retrieve data from `{search_url}`')
    logger.error(f'http status code: {status}')
    sys.exit(1)


async def fetch_page_async(url, session):
    """
    Async page fetch with exponential backoff
    """
    proxy = os.environ['HTTP_PROXY']

    for i in range(MAX_TRIES):
        logger.info(f'fetching data from `{url}` using proxy `{proxy}`')
        async with session.get(url) as response:
            status = response.status

            if status == 429 or str(status).startswith('5'):
                # exponential backoff
                wait_time = _backoff_wait_time(i)
                logger.warning(f'waiting `{wait_time}` before trying again')
                # I am using a blocking syncronous sleep instead of
                # asyncio.sleep because I want it to block and slow down all
                # concurrent requests
                time.sleep(wait_time)

            elif status == 200:
                return await response.text()

            else:  # I consider any other status code as an error
                break

    logger.error(f'could not retrieve data from `{search_url}`')
    logger.error(f'http status code: {status}')
    sys.exit(1)


async def fetch_many_pages_async(urls, loop):
    async with aiohttp.ClientSession(loop=loop, trust_env=True) as session:
        tasks = [fetch_page_async(url, session) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


def fetch_lang_stats(links):
    loop = asyncio.get_event_loop()
    pages = loop.run_until_complete(fetch_many_pages_async(links, loop))
    return map(parse_repo_lang_stats, pages)
