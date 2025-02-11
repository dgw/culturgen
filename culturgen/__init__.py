"""Know Your Meme scraper

License: MIT

Original `memedict` package copyright 2018 Fabrice Laporte
This rewrite copyright 2025 dgw
"""
from __future__ import annotations

from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from . import util

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


def search_meme(
    text: str,
    *,  # keyword-only after this point
    threshold: float | None = None,
    user_agent: str | None = None
) -> tuple[str, str] | tuple[None, None]:
    """Return a meme name and URL from keywords.

    :param text: The text to search for in the Know Your Meme database.
    :param threshold: Optional similarity threshold for a match to be considered
                      successful. Passed to :class:`difflib.SequenceMatcher`\\.
    :param user_agent: Optional custom user agent string to use in the headers.
    :return: A tuple of the meme name and URL, or a tuple of two ``None`` values
             if no close-enough match was found.
    """
    results = util.title_search(text, user_agent=user_agent)

    if not results:
        return None, None

    if threshold is None:
        # without a similarity threshold, just take the first result
        # relies on CPython's ordering dicts by insertion order
        return list(results.items())[0]

    # this is where it gets interesting
    scores = {k: SequenceMatcher(None, text, k).ratio() for k in results.keys()}
    try:
        title = max(filter(lambda k: scores[k] >= threshold, scores))
    except ValueError:
        # no results met the threshold
        return None, None
    else:
        return title, results[title]


def search(
    text: str,
    *,  # keyword-only after this point
    threshold: float | None = 0.4,
    user_agent: str | None = None,
) -> str | None:
    """Return a meme definition from keywords.

    :param text: The text to search for in the Know Your Meme database.
    :param threshold: Optional similarity threshold for a match to be considered
                      successful. Defaults to 0.4.
    """
    title, url = search_meme(text, threshold=threshold, user_agent=user_agent)
    if title and url:
        soup = util.get_meme(url, user_agent)
        return _format_meme_snippet(soup)


def fetch(
    slug_or_url: str,
    user_agent: str | None = None,
) -> str | None:
    """Fetch a meme definition from its slug or URL.

    :param slug_or_url: The slug or full KYM URL of the meme page to fetch.
    :param user_agent: Optional custom user agent string to use in the headers.
    """
    if (meme := util.get_meme(slug_or_url, user_agent)) is None:
        return None

    return _format_meme_snippet(meme)


def _format_meme_snippet(meme: BeautifulSoup) -> str | None:
    """Format the ``meme`` into a text snippet.

    :param meme: BeautifulSoup object representing the meme page.
    :return: A text snippet summarizing as much about the meme as possible, or
             ``None`` if no information could be extracted.
    """
    if (title := util.get_meme_title(meme)) is None:
        return None

    if not (about := util.extract_section_text(meme, 'about')):
        return f'{title}.'

    return f'{title}. {about}'
