"""Custom data types for the culturgen library.

Copyright (c) 2025 dgw

MIT License
"""
from __future__ import annotations

from collections import namedtuple

from . import util


TitleResult = namedtuple('TitleResult', ('title', 'url', 'ratio'))
"""A simple title-search result object.

:param title: The title of the search result.
:param url: The URL of the search result.
:param ratio: The similarity of the search result to the original query, as a
              float between 0 and 1.
"""


class Meme:
    """Object representing a meme entry on KYM.

    :param url: The URL or slug of the meme page to represent.
    :param user_agent: Optional custom user agent string to send when fetching
                       the page from KYM.
    :raises ValueError: If the meme page could not be fetched to instantiate the
                        new object.

    On object creation, fetches the meme page from Know Your Meme. Properties
    are lazily extracted from the HTML when first accessed.
    """
    def __init__(
        self,
        url: str,
        *,
        user_agent: str | None = None,
    ):
        self._url = (
            url if url.startswith(('http:', 'https:'))
            else 'https://knowyourmeme.com/memes/' + url
        )
        page = util.get_meme_page(self._url, user_agent)
        if page is None:
            raise ValueError(f'Failed to fetch meme page at {self._url}')
        self._page = page

    @property
    def url(self) -> str:
        """The URL of the meme page."""
        return self._url

    @property
    def title(self) -> str | None:
        """The title of the meme.

        Will be ``None`` if the title can't be extracted.
        """
        if not hasattr(self, '_title'):
            self._title = util.get_meme_title(self._page)

        return self._title or None

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

    def __repr__(self) -> str:
        return f'<Meme: {self.title!r}>'
