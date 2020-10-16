"""
Functions used in HTML parsing
"""

import logging

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def _could_not_parse(elem, ret_val=None):
    logger.warning('some html data could not be properly parsed...')
    return ret_val


def get_link(elem, gh_url):
    """
    Given an item from a set of repos, issues or wikis, return the link.
    As fas as I can tell, the right link always seems to be inside of a div
    with class f4 (and is the only link inside such div).
    I assume that's always the case.
    """
    if (div := elem.find('div', class_='f4')) and \
            (a := div.find('a', href=True)) and \
            (href := a.get('href')):
        return f'{gh_url}{href}'
    else:
        return _could_not_parse(div)


def get_repo_hits(div):
    """
    Given the `codesearch_results` for a repository search, return a list with
    the elements containing the repository links.
    It seems like the html structure of such results looks something like:

    <div class="codesearch-results">
      <div>
        <div>...</div>
        <ul class="repo-list">
          <li class="repo-list-item hx_hit-repo">...</li>
          <li class="repo-list-item hx_hit-repo">...</li>
          <li class="repo-list-item hx_hit-repo">...</li>
        </ul>
      <div>
    </div>

    I'll assume that's always the case
    """
    if elem_list := div.find("ul", class_="repo-list"):
        return elem_list.find_all("li", class_="hx_hit-repo")
    else:
        return _could_not_parse(div, [])


def get_issue_hits(div):
    """
    Given the `codesearch_results` for an issue search, return a list with
    the elements containing the issue links.
    It seems like the html structure of such results looks something like:

    <div class="codesearch-results">
      <div>
        <div>...</div>
        <div id="issue-search-results">
          <div class="issue-list">
            <div>
              <div class="issue-list-item hx_hit-issue">...</div>
              <div class="issue-list-item hx_hit-issue">...</div>
              <div class="issue-list-item hx_hit-issue">...</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    I'll assume that's always the case
    """
    if elem_list := div.find("div", class_="issue-list"):
        return elem_list.find_all("div", class_="hx_hit-issue")
    else:
        return _could_not_parse(div, [])


def get_wiki_hits(div):
    """
    Given the `codesearch_results` for a wiki search, return a list with
    the elements containing the wiki links.
    It seems like the html structure of such results looks something like:

    <div class="codesearch-results">
      <div>
        <div>...</div>
        <div id="wiki_search_results">
          <div>
            <div class="hx_hit-wiki">...</div>
            <div class="hx_hit-wiki">...</div>
            <div class="hx_hit-wiki">...</div>
          </div>
        </div>
      </div>
    </div>

    I'll assume that's always the case
    """
    if elem_list := div.find("div", id="wiki_search_results"):
        return elem_list.find_all("div", class_="hx_hit-wiki")
    else:
        return _could_not_parse(div, [])


HIT_GETTERS = {
    "repositories": get_repo_hits,
    "issues": get_issue_hits,
    "wikis": get_wiki_hits}


def parse_links(content, page_type, gh_url):
    """
    Given a BeautifulSoup object and a function to retrieve the git elements,
    return a list of links
    """
    hit_getter = HIT_GETTERS[page_type]
    soup = BeautifulSoup(content, 'html.parser')
    if codesearch_results := soup.find("div", class_="codesearch-results"):
        hits = hit_getter(codesearch_results)
        links = [
            link
            for elem in hits
            if (link := get_link(elem, gh_url)) is not None]
        return links
    else:
        return _could_not_parse(soup, [])


def parse_lang_stat(elem):
    """
    Parse a BeautifulSoup object corresponding to an element containing the
    stat of a specific language into a tuple.
    I assume a structure like so:
    <li>
      <a>(or <span>)
        ...
        <span>(language name)</span>
        <span>(language stat)%</span>
      </a>(or </span>)
    </li>
    """
    if a := elem.find(['a', 'span']):
        try:
            lang, stat = a.find_all('span')
        except ValueError:
            return _could_not_parse(a)
        else:
            try:
                stat_val = float(stat.text.replace('%', ''))
            except ValueError:
                return _could_not_parse(stat)
            else:
                return lang.text, stat_val
    else:
        return _could_not_parse(elem)


def parse_repo_lang_stats(content):
    """
    Parse the language stats from a given repo HTML content.
    I assume a stucture like so:

    <div>
      <h2>Languages</h2>
      <div>...</div>
      <ul>
        </li>(language stats)<li>
        </li>(language stats)<li>
        </li>(language stats)<li>
      </ul>
    </div>

    If there's no <h2>Languages</h2>, I assume that repo doesn't have language
    stats there won't be any warning
    """
    soup = BeautifulSoup(content, 'html.parser')
    if h2 := soup.find("h2", string="Languages"):
        if (ul := h2.find_next('ul')):
            stats = dict(
                stat
                for li in ul.find_all('li')
                if (stat := parse_lang_stat(li)) is not None)
            return stats
        else:
            return _could_not_parse(soup, dict())
    else:
        return dict()
