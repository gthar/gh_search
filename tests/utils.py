import contextlib
import io
import logging
import os
import tempfile
import textwrap
import unittest

from unittest.mock import patch, mock_open

from asynctest import CoroutineMock

from gh_search.utils import (
    get_owner, set_proxy, read_input, write_output, gh_search)


class MockResponse:
    def __init__(self, content, status_code=200):
        self.content = content.encode('utf-8')
        self.status_code = status_code


class TestUtils(unittest.TestCase):

    def setUp(self):
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_get_owner(self):
        self.assertEqual(get_owner('github.com//foo/bar'), 'foo')
        self.assertEqual(get_owner('github.com/foo//bar'), 'foo')
        self.assertEqual(get_owner('github.com/foo//bar/qux'), 'foo')
        self.assertEqual(get_owner('github.com/foo/bar'), 'foo')
        self.assertEqual(get_owner('http://github.com/foo/bar'), 'foo')
        self.assertEqual(get_owner('http://www.github.com/foo/bar'), 'foo')
        self.assertEqual(get_owner('https://github.com/foo/bar'), 'foo')
        self.assertEqual(get_owner('https://www.github.com/foo/bar'), 'foo')
        self.assertEqual(get_owner('www.github.com/foo/bar'), 'foo')

    def test_set_proxy(self):
        proxies = [
            '188.28.254.196',
            '48.182.70.155',
            '78.7.85.151',
            '57.138.79.2']
        # I don't like that this test is not deterministic, so I'll run it a
        # few times even if it's somewhat trivial
        for _ in range(10):
            set_proxy(proxies)
            self.assertIn(os.environ['HTTP_PROXY'], proxies)


class TestReadInput(unittest.TestCase):

    def setUp(self):
        logging.getLogger().setLevel(logging.CRITICAL)

    @patch('builtins.open')
    def test_read_input(self, open):
        data = textwrap.dedent("""
            {
              "keywords": ["foo", "bar"],
              "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
              "type": "Repositories"
            }
        """).strip()
        open.side_effect = mock_open(read_data=data)
        keywords, proxies, page_type = read_input('mock')
        self.assertEqual(keywords, ['foo', 'bar'])
        self.assertEqual(proxies, ["194.126.37.94:8080", "13.78.125.167:8080"])
        self.assertEqual(page_type, "repositories")

    @patch('builtins.open')
    def test_read_input_badjson(self, open):
        data = textwrap.dedent("""
            {
              "keywords": foo", "bar"],
              "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
              "type": "Repositories"
            }
        """).strip()
        open.side_effect = mock_open(read_data=data)
        with self.assertRaises(SystemExit):
            read_input('mock')

    @patch('builtins.open')
    def test_read_input_badtype(self, open):
        data = textwrap.dedent("""
            {
              "keywords": ["foo", "bar"],
              "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
              "type": "positories"
            }
        """).strip()
        open.side_effect = mock_open(read_data=data)
        with self.assertRaises(SystemExit):
            read_input('mock')

    @patch('builtins.open')
    def test_read_input_missingparam(self, open):
        data = textwrap.dedent("""
            {
              "keywords": ["foo", "bar"],
              "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"]
            }
        """).strip()
        open.side_effect = mock_open(read_data=data)
        with self.assertRaises(SystemExit):
            read_input('mock')

    def test_write_output(self):
        outfile = tempfile.NamedTemporaryFile(mode='w+')
        write_output(['foo'], outfile.name)
        self.assertEqual(outfile.read(), '[\n  "foo"\n]')

    def test_write_output_stdout(self):
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                write_output(['foo'])
            self.assertEqual(buf.getvalue(), '[\n  "foo"\n]')


class TestGHSearch(unittest.TestCase):

    @patch('aiohttp.ClientSession.get')
    @patch('requests.get')
    def test_gh_search(self, get, async_get):
        get.return_value = MockResponse("""
            <div class="codesearch-results">
              <div>
                <ul class="repo-list">
                  <li class="repo-list-item hx_hit-repo">
                    <div class="f4"><a href="/foo/bar">foo</a></div>
                  </li>
                </ul>
              <div>
            </div>
        """)
        async_get.return_value.__aenter__.return_value.status = 200
        async_get.return_value.__aenter__.return_value.text = CoroutineMock(
            return_value="""
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
            """
        )
        result = gh_search(['foo', 'bar'], 'repositories', 'http://github.com')
        expected = [{
            'url': 'http://github.com/foo/bar',
            'extra': {'owner': 'foo', 'language_stats': {'Rust': 100.0}}}]
        self.assertEqual(result, expected)

    @patch('requests.get')
    def test_gh_search_issue(self, get):
        get.return_value = MockResponse("""
            <div class="codesearch-results">
              <div>
                <div id="issue-rearch-results">
                  <div class="issue-list">
                    <div>
                      <div class="issue-list-item hx_hit-issue">
                        <div>
                          <div class="f4">
                            <a href="/mock">foo</a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        """)
        result = gh_search(['foo', 'bar'], 'issues', 'http://github.com')
        expected = [{'url': 'http://github.com/mock'}]
        self.assertEqual(result, expected)
