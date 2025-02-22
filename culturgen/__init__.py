"""Know Your Meme scraper

License: MIT

Original `memedict` package copyright 2018 Fabrice Laporte
This rewrite copyright 2025 dgw
"""
from __future__ import annotations

from . import util
from .types import Meme


def search_meme(
    text: str,
    *,  # keyword-only after this point
    threshold: float | None = None,
    user_agent: str | None = None
) -> Meme | None:
    """Get a :class:`~.types.Meme` object from keywords.

    :param text: The text to search for in the Know Your Meme database.
    :param threshold: Optional similarity threshold for a match to be considered
                      successful. Valid range of 0.0 to 1.0, inclusive.
    :param user_agent: Optional custom user agent string to use in the headers.
    :return: A :class:`~.types.Meme` object representing the meme page, or
             ``None`` if no close enough result was found.
    :raises ValueError: If ``threshold`` is outside the valid range.
    """
    if not (results := util.title_search(text, user_agent=user_agent)):
        return None

    if threshold is None:
        # without a similarity threshold, just take the generator's first item
        return Meme(next(results).url)

    if threshold < 0.0 or threshold > 1.0:
        raise ValueError('threshold must be in the range [0.0, 1.0]')

    # this is where it gets interesting
    ranked = sorted(
        filter(lambda res: res.ratio >= threshold, results),
        key=lambda res: res.ratio,
        reverse=True,
    )
    if ranked:
        return Meme(ranked[0].url)
    return None


def search(
    text: str,
    *,  # keyword-only after this point
    threshold: float | None = 0.5,
    user_agent: str | None = None,
) -> str | None:
    """Return a meme definition from keywords.

    :param text: The text to search for in the Know Your Meme database.
    :param threshold: Optional similarity threshold for title matches. Valid
                      range of 0.0 to 1.0, inclusive. Defaults to ``0.5``; pass
                      ``threshold=None`` to disable.
    """
    if (meme := search_meme(
        text,
        threshold=threshold,
        user_agent=user_agent
    )) is None:
        return None

    return _format_meme_snippet(meme)


def fetch_meme(
    slug_or_url: str,
    user_agent: str | None = None,
) -> Meme | None:
    """Get a :class:`.types.Meme` object from its slug or URL.

    :param slug_or_url: The slug or full KYM URL of the meme page to fetch.
    :param user_agent: Optional custom user agent string to use in the headers.
    :return: A :class:`~.types.Meme` object representing the meme page, or
             ``None`` if the meme page couldn't be fetched.
    """
    try:
        return util.get_meme(slug_or_url, user_agent=user_agent)
    except ValueError:
        return None


def fetch(
    slug_or_url: str,
    user_agent: str | None = None,
) -> str | None:
    """Fetch a meme definition from its slug or URL.

    :param slug_or_url: The slug or full KYM URL of the meme page to fetch.
    :param user_agent: Optional custom user agent string to use in the headers.
    """
    try:
        meme = util.get_meme(slug_or_url, user_agent)
    except ValueError:
        return None

    return _format_meme_snippet(meme)


def _format_meme_snippet(meme: Meme) -> str | None:
    """Format the ``meme`` into a text snippet.

    :param meme: :class:`~.types.Meme` object representing the meme page.
    :return: A text snippet summarizing as much about the meme as possible, or
             ``None`` if no information could be extracted.
    """
    if not (title := meme.title):
        return None

    if not (about := meme.about):
        return f'{title}.'

    return f'{title}. {about}'
