import asyncio
import logging
import os
import unittest

from unittest.mock import patch, MagicMock

from asynctest import CoroutineMock

from gh_search.fetchers import (
    fetch_links, fetch_many_pages_async, fetch_lang_stats)


class MockResponse:
    def __init__(self, content, status_code=200):
        self.content = content.encode('utf-8')
        self.status_code = status_code


class TestFetchers(unittest.TestCase):

    def setUp(self):
        os.environ['HTTP_PROXY'] = 'proxy.mock'
        logging.getLogger().setLevel(logging.CRITICAL)

    @patch('requests.get')
    def test_fetch_links(self, get):
        get.return_value = MockResponse("""
            <div class="codesearch-results">
              <div>
                <ul class="repo-list">
                  <li class="repo-list-item hx_hit-repo">
                    <div class="f4"><a href="/foo">foo</a></div>
                  </li>
                  <li class="repo-list-item hx_hit-repo">
                    <div class="f4"><a href="/bar">bar</a></div>
                  </li>
                  <li class="repo-list-item hx_hit-repo">
                    <div class="f4"><a href="/qux">qux</a></div>
                  </li>
                </ul>
              <div>
            </div>
        """)
        expected = [
            'https://github.com/foo',
            'https://github.com/bar',
            'https://github.com/qux']
        result = fetch_links(
            ['foo', 'bar'],
            'repositories',
            'https://github.com')
        self.assertEqual(expected, result)

    @patch('requests.get')
    def test_fetch_links_error(self, get):
        get.return_value = MockResponse("mock", 404)
        with self.assertRaises(SystemExit):
            fetch_links(['foo', 'bar'], 'repositories', 'https://github.com')

    @patch('time.sleep')  # I am pathing sleep to speed things up
    @patch('requests.get')
    def test_fetch_links_backoff(self, get, sleep):
        get.side_effect = [
            MockResponse("wait for it", 429),
            MockResponse("wait more", 503),
            MockResponse("""
                <div class="codesearch-results">
                  <div>
                    <ul class="repo-list">
                      <li class="repo-list-item hx_hit-repo">
                        <div class="f4"><a href="/foo">foo</a></div>
                      </li>
                      <li class="repo-list-item hx_hit-repo">
                        <div class="f4"><a href="/bar">bar</a></div>
                      </li>
                      <li class="repo-list-item hx_hit-repo">
                        <div class="f4"><a href="/qux">qux</a></div>
                      </li>
                    </ul>
                  <div>
                </div>
            """)]
        expected = [
            'https://github.com/foo',
            'https://github.com/bar',
            'https://github.com/qux']
        result = fetch_links(
            ['foo', 'bar'],
            'repositories',
            'https://github.com')
        self.assertEqual(expected, result)
        self.assertEqual(get.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch('time.sleep')
    @patch('requests.get')
    def test_fetch_links_backoff_error(self, get, sleep):
        get.return_value = MockResponse("just keep waiting...", 429)
        with self.assertRaises(SystemExit):
            fetch_links(['foo', 'bar'], 'repositories', 'https://github.com')
        self.assertEqual(get.call_count, 10)
        self.assertEqual(sleep.call_count, 10)

    @patch('aiohttp.ClientSession.get')
    def test_fetch_many_pages_async(self, get):
        get.return_value.__aenter__.return_value.status = 200
        get.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=['foo', 'bar'])  # noqa
        loop = asyncio.get_event_loop()
        task = fetch_many_pages_async(
            ['https://github.com/foo/bar', 'https://github.com/foo/qux'],
            loop)
        result = loop.run_until_complete(task)
        self.assertEqual(['foo', 'bar'], result)

    @patch('aiohttp.ClientSession.get')
    def test_fetch_many_pages_async_error(self, get):
        get.return_value.__aenter__.return_value.status = 404
        get.return_value.__aenter__.return_value.text = CoroutineMock(return_value='foo')  # noqa
        loop = asyncio.get_event_loop()
        task = fetch_many_pages_async(['https://github.com/foo/bar'], loop)
        with self.assertRaises(SystemExit):
            loop.run_until_complete(task)

    @patch('time.sleep')
    @patch('aiohttp.ClientSession.get')
    def test_fetch_many_pages_async_backoff(self, get, sleep):
        get.return_value.__aenter__.side_effect = [
            MagicMock(
                status=429,
                text=CoroutineMock(return_value='wait for it')),
            MagicMock(
                status=503,
                text=CoroutineMock(return_value='wait more')),
            MagicMock(
                status=200,
                text=CoroutineMock(return_value="good"))]
        loop = asyncio.get_event_loop()
        task = fetch_many_pages_async(['https://github.com/foo/bar'], loop)
        result = loop.run_until_complete(task)
        self.assertEqual(result, ["good"])
        self.assertEqual(get.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch('time.sleep')
    @patch('aiohttp.ClientSession.get')
    def test_fetch_many_pages_async_backoff_error(self, get, sleep):
        get.return_value.__aenter__.return_value.text = CoroutineMock(return_value="just keep waiting...")  # noqa
        get.return_value.__aenter__.return_value.status = 429
        loop = asyncio.get_event_loop()
        task = fetch_many_pages_async(['https://github.com/foo/bar'], loop)
        with self.assertRaises(SystemExit):
            loop.run_until_complete(task)
        self.assertEqual(get.call_count, 10)
        self.assertEqual(sleep.call_count, 10)

    @patch('aiohttp.ClientSession.get')
    def test_fetch_lang_stats(self, get):
        get.return_value.__aenter__.return_value.status = 200
        get.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=[  # noqa
            """
                <div>
                  <h2>Languages</h2>
                  <ul>
                    <li>
                      <a>
                        <span>Rust</span>
                        <span>100%</span>
                      </a>
                    </li>
                  </ul>
                </div>
            """,
            """
                <div>
                  <h2>Languages</h2>
                  <ul>
                    <li>
                      <a>
                        <span>Go</span>
                        <span>100%</span>
                      </a>
                    </li>
                  </ul>
                </div>
            """
        ])
        expected = [{'Rust': 100.0}, {'Go': 100.0}]
        result = list(fetch_lang_stats([
            'https://github.com/foo/bar', 'https://github.com/foo/qux']))
        self.assertEqual(expected, result)
