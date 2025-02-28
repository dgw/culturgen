"""Custom data types for the culturgen library.

Copyright (c) 2025 dgw

MIT License
"""
from __future__ import annotations

from collections import namedtuple

from bs4 import BeautifulSoup
import requests

from . import util


TitleResult = namedtuple('TitleResult', ('title', 'url', 'ratio'))
"""A simple title-search result object.

:param title: The title of the search result.
:param url: The URL of the search result.
:param ratio: The similarity of the search result to the original query, as a
              float between 0 and 1.
"""


class AbstractEntry:
    """Object representing an entry on KYM.

    :param url: The URL or slug of the entry page to represent.
    :param user_agent: Optional custom user agent string to send when fetching
                       the page from KYM.
    :raises ValueError: If the page couldn't be fetched to instantiate the new
                        object.

    On object creation, fetches the page from Know Your Meme. Properties are
    lazily extracted from the HTML when first accessed.

    Creating an object of type other than :class:`Meme` by slug may or may not
    work depending on subtype. KYM has to redirect ``/memes/:slug`` to
    ``/memes/:type/:slug`` for us.
    """
    _prefix = 'https://knowyourmeme.com/memes/'
    # The URL prefix for meme pages on KYM.

    def __init__(
        self,
        url: str,
        *,
        user_agent: str | None = None,
    ):
        if url.startswith('https:'):
            self._url = url
        elif url.startswith('http:'):
            self._url = 'https:' + url.removeprefix('http:')
        else:
            self._url = self._prefix + url

        r = requests.get(self._url, headers=util.get_headers(user_agent))
        if r.status_code != 200:
            raise ValueError(f'Failed to fetch entry page at {self._url}')

        self._page = BeautifulSoup(r.text, 'html.parser')
        self._url = r.url  # account for any redirects

    @property
    def url(self) -> str:
        """The URL of the entry page."""
        return self._url

    @property
    def title(self) -> str | None:
        """The title of the entry.

        Will be ``None`` if the title can't be extracted.
        """
        if not hasattr(self, '_title'):
            self._title = util.get_meme_title(self._page)

        return self._title or None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.title!r}>'


class Meme(AbstractEntry):
    @property
    def about(self) -> str | None:
        """The "about" section of the meme page.

        Returns the first string that can be found from the following list:

        1. The text of the "about" section.
        2. The first paragraph of the entry body.

        Will be ``None`` if no text can be extracted.
        """
        if not hasattr(self, '_about'):
            self._about = (
                util.extract_section_text(self._page, 'about')
                or getattr(self._page.select_one('#entry_body p'), 'text', None)
            )

        return self._about or None


class Event(AbstractEntry):
    _prefix = 'https://knowyourmeme.com/memes/events/'
    # The URL prefix for event pages on KYM.

    @property
    def overview(self) -> str | None:
        """An overview of the event page.

        Returns the first string that can be found from the following list:

        1. The text of the "Overview" section.
        2. The first paragraph of the entry body.

        Will be ``None`` if no text can be extracted.
        """
        if not hasattr(self, '_overview'):
            self._about = (
                util.extract_section_text(self._page, 'overview')
                or getattr(self._page.select_one('#entry_body p'), 'text', None)
            )

        return self._overview or None
