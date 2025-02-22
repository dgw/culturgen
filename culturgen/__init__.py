"""Know Your Meme scraper

License: MIT

Original `memedict` package copyright 2018 Fabrice Laporte
This rewrite copyright 2025 dgw
"""
from difflib import SequenceMatcher

from bs4 import BeautifulSoup
import requests


SEARCH_SIMILARITY_THRESHOLD = .4

HEADERS = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')}


def search_meme(text, user_agent=None):
    """Return a meme name and URL from keywords."""
    r = requests.get(
        'https://knowyourmeme.com/search?q=%s' % text,
        headers=_make_headers(user_agent)
    )
    soup = BeautifulSoup(r.text, 'html.parser')
    result = soup.find('a', class_='item', href=True)
    if result:
        return result['data-title'], result['href']
    return None, None


def search(text, user_agent=None):
    """Return a meme definition from keywords."""
    meme_name, url = search_meme(text, user_agent=user_agent)
    if meme_name and SequenceMatcher(
        # .lower() is needed to make the comparison case-insensitive
        # otherwise the ratio for e.g. 'OMGWTFBBQ' and 'omgwtfbbq' is 0.0
        None, text.lower(), meme_name.lower()
    ).ratio() >= SEARCH_SIMILARITY_THRESHOLD:
        r = requests.get(url, headers=_make_headers(user_agent))
        soup = BeautifulSoup(r.text, 'html.parser')
        entry = soup.find('h2', {'id': 'about'})
        return '%s. %s' % (meme_name.split('/')[-1].title(), entry.next.next.next.text)


def _make_headers(user_agent=None):
    """Build request headers using the given ``user_agent``."""
    # don't modify the default headers dict!
    headers = HEADERS.copy()

    if user_agent:
        headers['User-Agent'] = user_agent

    return headers
