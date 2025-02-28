"""Utility functions for the culturgen library."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from jellyfish import jaro_winkler_similarity as jw_ratio
import requests

from .types import AbstractEntry, Event, Meme, TitleResult

if TYPE_CHECKING:
    from typing import Generator


DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    ),
}


def get_headers(user_agent: str | None = None) -> dict[str, str]:
    """Build request headers using the given ``user_agent``.

    :param user_agent: Optional user agent string to use in the headers. If not
                       specified, the default user agent (an old version of
                       Chrome on macOS) will be used.
    :return: A dictionary of standard headers to send with HTTP requests.
    """
    # never modify the DEFAULT_HEADERS dict
    # the changes WILL bleed through to future calls
    headers = DEFAULT_HEADERS.copy()

    if user_agent:
        headers['User-Agent'] = user_agent

    return headers


def get_meme(
    slug_or_url: str,
    user_agent: str | None = None,
) -> AbstractEntry:
    """Get an entry from its slug or URL.

    :param slug_or_url: The slug or full KYM URL of the entry page to fetch.
    :param user_agent: Optional custom user agent string to use in the headers.
    :return: A :class:`~.types.AbstractEntry` subtype representing the page.
    :raises ValueError: If the object couldn't instantiate itself (probably
                        because the given page doesn't exist).
    """
    return Meme(slug_or_url, user_agent=user_agent)


def get_meme_page(
    slug_or_url: str,
    user_agent: str | None = None,
) -> BeautifulSoup | None:
    """Get an entry page object from its slug or URL.

    :param slug_or_url: The slug or full KYM URL of the entry page to fetch.
    :param user_agent: Optional custom user agent string to use in the headers.
    :return: A BeautifulSoup object representing the entry page, or ``None`` if
             the page couldn't be fetched.

    This function relies on KYM redirecting ``/memes/:slug`` to
    ``/memes/:type/:slug`` for us if necessary. Subtypes that don't do so won't
    work with this function.
    """
    if slug_or_url.startswith('https:'):
        url = slug_or_url
    elif slug_or_url.startswith('http:'):
        url = 'https:' + slug_or_url.removeprefix('http:')
    else:
        url = 'https://knowyourmeme.com/memes/' + slug_or_url

    r = requests.get(url, headers=get_headers(user_agent))
    if r.status_code != 200:
        return None

    return BeautifulSoup(r.text, 'html.parser')


def extract_section_text(soup, section_id: str) -> str | None:
    """Extract the text of a section from a Know Your Meme page.

    :param soup: BeautifulSoup object representing the page to extract from.
    :param section_id: ID of the section to extract.
    :return: The text contents of all paragraphs in the section, or ``None`` if
             the ``section_id`` isn't found. Inserts spaces between paragraphs.
    """
    section = soup.css.select(f'#{section_id} ~ p:not([id!={section_id}] ~ *)')
    if not section:
        return None

    out = ''
    for p in section:
        out += p.text + ' '

    return out.rstrip()


# "About" is the most common section needed, so it gets a dedicated function.
def get_meme_about(soup: BeautifulSoup) -> str | None:
    """Return the "about" section text for a meme page.

    :param meme: BeautifulSoup object representing the meme page.
    :return: The text contents of the "about" section, or ``None`` if the
             section wasn't found.
    """
    if not (about := extract_section_text(soup, 'about')):
        return None

    return about


def get_meme_title(soup: BeautifulSoup) -> str | None:
    """Return the title of a meme page.

    :param meme: BeautifulSoup object representing the meme page.
    :return: The title of the meme, or ``None`` if the title wasn't found.
    """
    if (title := soup.find('h1', class_='entry-title')) is None:
        return None

    # BS4 tags include ALL children in .text and .string, even whitespace that a
    # browser would collapse. Using `stripped_strings` like this is less likely
    # to include junk.
    return ' '.join(title.stripped_strings)


def title_search(
    query: str,
    user_agent: str | None = None,
) -> Generator[TitleResult, None, None]:
    """Search Know Your Meme by title keywords.

    :param query: The search keyword(s).
    :param user_agent: Optional custom user agent string to use in the headers.
    :return: An :term:`iterable` of up to 10 :class:`TitleResult` tuples.

    This function uses the "quick links" endpoint from KYM's search bar. On the
    one hand, that isn't a public API, so it could break at any time. On the
    other hand… HTML scraping can break too, if the page structure changes.

    Results are filtered to only include standard meme pages (not under subpaths
    like ``/memes/people/``).
    """
    r = requests.get(
        # uses http:// instead of https:// on purpose
        # their SSL config raises DH_KEY_TOO_SMALL errors on up-to-date envs
        'http://rkgk.api.searchify.com/v1/indexes/kym_production/instantlinks',
        headers=get_headers(user_agent),
        params={
            'query': query,
            'field': 'name',
            'fetch': 'name,url',
            'len': '10',
        },
    )
    try:
        data = r.json()
    except ValueError:
        return

    yield from (
        TitleResult(
            item['name'],
            'https://knowyourmeme.com' + item['url'],
            # .lower()ing both makes the similarity check case-insensitive,
            # which is better for most use cases (e.g. users lazily typing
            # queries in all lowercase)
            jw_ratio(query.lower(), item['name'].lower()),
        )
        for item in data['results']
        if re.match(r'/memes/[^/]+/?$', item['url'], re.I)
    )
