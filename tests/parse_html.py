import unittest
import logging

from bs4 import BeautifulSoup

from gh_search.parse_html import (
    get_link, get_repo_hits, get_issue_hits, get_wiki_hits, parse_links,
    parse_lang_stat, parse_repo_lang_stats)


class TestParseHTML(unittest.TestCase):

    def setUp(self):
        logging.getLogger().setLevel(logging.ERROR)

    def test_get_link(self):
        mock = """
        <div>
            <div class="f4">
                <a href="/mock">foo</a>
            </div>
        </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        expected = "https://github.com/mock"
        self.assertEqual(get_link(soup, 'https://github.com'), expected)

    def test_get_link_none(self):
        mock = """
        <div>
            <div>
                <a href="/mock">foo</a>
            </div>
        </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertIsNone(get_link(soup, 'https://github.com'))

        mock = """
        <div>
            <div class="f4">
            </div>
        </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertIsNone(get_link(soup, 'https://github.com'))

        mock = """
        <div>
            <div class="f4">
                <a>foo</a>
            </div>
        </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertIsNone(get_link(soup, 'https//github.com'))

    def test_get_repo_hits(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <ul class="repo-list">
                  <li class="repo-list-item hx_hit-repo">foo</li>
                  <li class="repo-list-item hx_hit-repo">bar</li>
                  <li class="repo-list-item hx_hit-repo">qux</li>
                </ul>
              <div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        expected = [
            '<li class="repo-list-item hx_hit-repo">foo</li>',
            '<li class="repo-list-item hx_hit-repo">bar</li>',
            '<li class="repo-list-item hx_hit-repo">qux</li>']
        self.assertEqual(expected, list(map(str, get_repo_hits(soup))))

    def test_get_repo_hits_none(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <ul>
                  <li class="repo-list-item hx_hit-repo">foo</li>
                  <li class="repo-list-item hx_hit-repo">bar</li>
                  <li class="repo-list-item hx_hit-repo">qux</li>
                </ul>
              <div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertEqual([], get_repo_hits(soup))

        mock = """
            <div class="codesearch-results">
              <div>
                <ul>
                </ul>
              <div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertEqual([], get_repo_hits(soup))

        mock = """
            <div class="codesearch-results">
              <div>
              </div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertEqual([], get_repo_hits(soup))

    def test_get_issue_hits(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <div>...</div>
                <div id="issue-search-results">
                  <div class="issue-list">
                    <div>
                      <div class="issue-list-item hx_hit-issue">foo</div>
                      <div class="issue-list-item hx_hit-issue">bar</div>
                      <div class="issue-list-item hx_hit-issue">qux</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        expected = [
            '<div class="issue-list-item hx_hit-issue">foo</div>',
            '<div class="issue-list-item hx_hit-issue">bar</div>',
            '<div class="issue-list-item hx_hit-issue">qux</div>']
        self.assertEqual(expected, list(map(str, get_issue_hits(soup))))

    def test_get_issue_hits_none(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <div>...</div>
                <div id="issue-search-results">
                  <div>
                    <div>
                      <div class="issue-list-item hx_hit-issue">foo</div>
                      <div class="issue-list-item hx_hit-issue">bar</div>
                      <div class="issue-list-item hx_hit-issue">qux</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertEqual([], get_issue_hits(soup))

        mock = """
            <div class="codesearch-results">
              <div>
                <div>...</div>
                <div id="issue-search-results">
                  <div class="issue-list">
                  </div>
                </div>
              </div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertEqual([], get_issue_hits(soup))

    def test_get_wiki_hits(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <div id="wiki_search_results">
                  <div>
                    <div class="hx_hit-wiki">foo</div>
                    <div class="hx_hit-wiki">bar</div>
                    <div class="hx_hit-wiki">qux</div>
                  </div>
                </div>
              </div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        expected = [
            '<div class="hx_hit-wiki">foo</div>',
            '<div class="hx_hit-wiki">bar</div>',
            '<div class="hx_hit-wiki">qux</div>']
        self.assertEqual(expected, list(map(str, get_wiki_hits(soup))))

    def test_get_wiki_hits_none(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <div>
                  <div>
                    <div class="hx_hit-wiki">foo</div>
                    <div class="hx_hit-wiki">bar</div>
                    <div class="hx_hit-wiki">qux</div>
                  </div>
                </div>
              </div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertEqual([], get_wiki_hits(soup))

        mock = """
            <div class="codesearch-results">
              <div>
                <div id="wiki_search_results">
                  <div>
                  </div>
                </div>
              </div>
            </div>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertEqual([], get_wiki_hits(soup))

    def test_parse_links_repo(self):
        mock = """
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
        """
        expected = [
            'https://github.com/foo',
            'https://github.com/bar',
            'https://github.com/qux']
        result = parse_links(mock, "repositories", 'https://github.com')
        self.assertEqual(expected, result)

    def test_parse_links_issue(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <div class="issue-list">
                  <div class="issue-list-item hx_hit-issue">
                    <div class="f4"><a href="/foo">foo</a></div>
                  </div>
                  <div class="issue-list-item hx_hit-issue">
                    <div class="f4"><a href="/bar">bar</a></div>
                  </div>
                  <div class="issue-list-item hx_hit-issue">
                    <div class="f4"><a href="/qux">qux</a></div>
                  </div>
                </div>
              <div>
            </div>
        """
        expected = [
            'https://github.com/foo',
            'https://github.com/bar',
            'https://github.com/qux']
        result = parse_links(mock, "issues", 'https://github.com')
        self.assertEqual(expected, result)

    def test_parse_links_wikis(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <div id="wiki_search_results">
                  <div>
                    <div class="hx_hit-wiki">
                      <div class="f4"><a href="/foo">foo</a></div>
                    </div>
                    <div class="hx_hit-wiki">
                      <div class="f4"><a href="/bar">bar</a></div>
                    </div>
                    <div class="hx_hit-wiki">
                      <div class="f4"><a href="/qux">qux</a></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        """
        expected = [
            'https://github.com/foo',
            'https://github.com/bar',
            'https://github.com/qux']
        result = parse_links(mock, "wikis", 'https://github.com')
        self.assertEqual(expected, result)

    def test_parse_links_missing(self):
        mock = """
            <div class="codesearch-results">
              <div>
                <ul class="repo-list">
                  <li class="repo-list-item hx_hit-repo">
                    <div class="f4"><a href="/foo">foo</a></div>
                  </li>
                  <li class="repo-list-item hx_hit-repo">
                    <div class="f4"><a>bar</a></div>
                  </li>
                  <li class="repo-list-item hx_hit-repo">
                    <div class="f4"><a href="/qux">qux</a></div>
                  </li>
                </ul>
              <div>
            </div>
        """
        expected = [
            'https://github.com/foo',
            'https://github.com/qux']
        result = parse_links(mock, 'repositories', 'https://github.com')
        self.assertEqual(expected, result)

        mock = """
            <div class="codesearch-results">
              <div>
                <div class="issue-list">
                  <div class="issue-list-item hx_hit-issue">
                    <div class="f4"><a href="/foo">foo</a></div>
                  </div>
                  <div class="issue-list-item hx_hit-issue">
                    <div class="f4"><a href="/bar">bar</a></div>
                  </div>
                  <div>
                    <div class="f4"><a href="/qux">qux</a></div>
                  </div>
                </div>
              <div>
            </div>
        """
        expected = [
            'https://github.com/foo',
            'https://github.com/bar']
        result = parse_links(mock, 'issues', 'https://github.com')
        self.assertEqual(expected, result)

        mock = """
            <div class="codesearch-results">
            </div>
        """
        self.assertEqual([], parse_links(mock, 'wikis', 'https://github.com'))

        mock = "<div></div>"
        result = parse_links(mock, 'repositories', 'https://github.com')
        self.assertEqual([], result)

    def test_parse_lang_stat(self):
        mock = """
            <li>
              <a>
                <svg></svg>
                <span>Haskell</span>
                <span>100%</span>
              </a>
            </li>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        expected = ('Haskell', 100.0)
        self.assertEqual(expected, parse_lang_stat(soup))

    def test_parse_lang_stat_none(self):
        mock = """
            <li>
              <a>
                <svg></svg>
                <span>100%</span>
              </a>
            </li>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertIsNone(parse_lang_stat(soup))

        mock = """
            <li>
              <a>
                <span>Clojure</span>
                <span>10f%</span>
              </a>
            </li>
        """
        soup = BeautifulSoup(mock, 'html.parser')
        self.assertIsNone(parse_lang_stat(soup))

    def test_parse_repo_lang_stats(self):
        mock = """
            <div>
              <h2>Languages</h2>
              <div>...</div>
              <ul>
                <li>
                  <a>
                    <span>F#</span>
                    <span>25%</span>
                  </a>
                </li>
                <li>
                  <a>
                    <span>Scheme</span>
                    <span>50%</span>
                  </a>
                </li>
                <li>
                  <span>
                    <span>Others</span>
                    <span>25%</span>
                  </span>
                </li>
              </ul>
            </div>
        """
        expected = {
            'F#': 25.0,
            'Scheme': 50.0,
            'Others': 25.0}
        self.assertEqual(expected, parse_repo_lang_stats(mock))

    def test_parse_repo_lang_stats_missing(self):
        mock = """
            <div>
              <h2>Languages</h2>
              <div>...</div>
              <ul>
                <li>
                  <a>
                    <span>25%</span>
                  </a>
                </li>
                <li>
                  <a>
                    <span>Elixir</span>
                    <span>50%</span>
                  </a>
                </li>
                <li>
                  <a>
                    <span>Scala</span>
                    <span>25%</span>
                  </a>
                </li>
              </ul>
            </div>
        """
        expected = {
            'Elixir': 50.0,
            'Scala': 25.0}
        self.assertEqual(expected, parse_repo_lang_stats(mock))

    def test_parse_repo_lang_stats_none(self):
        mock = """
            <div>
              <div>...</div>
              <ul>
                <li>
                  <a>
                    <span>25%</span>
                  </a>
                </li>
                <li>
                  <a>
                    <span>Clojure</span>
                    <span>50%</span>
                  </a>
                </li>
                <li>
                  <a>
                    <span>F#</span>
                    <span>25%</span>
                  </a>
                </li>
              </ul>
            </div>
        """
        self.assertEqual({}, parse_repo_lang_stats(mock))
