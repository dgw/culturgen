"""Utility functions for the culturgen library."""
from __future__ import annotations

from bs4 import BeautifulSoup
import requests


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
) -> BeautifulSoup | None:
    """Get a meme page object from its slug or URL.

    :param slug_or_url: The slug or full KYM URL of the meme page to fetch.
    :param user_agent: Optional custom user agent string to use in the headers.
    :return: A BeautifulSoup object representing the meme page, or ``None`` if
             the page couldn't be fetched.
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


def extract_section_text(soup: BeautifulSoup, section_id: str) -> str | None:
    """Extract the text of a section from a Know Your Meme page.

    :param soup: BeautifulSoup object representing the page to extract from.
    :param section_id: ID of the section to extract.
    :return: The text contents of all paragraphs in the section, or ``None`` if
             the ``section_id`` isn't found. Inserts spaces between paragraphs.
    """
    # Some of this implementation was generated with help from Claude, as a
    # constrained experiment to see how "AI" (note: still basically just a giant
    # autocomplete) tools are evolving. I wrote an original implementation using
    # CSS selectors that didn't work very well, concluded that it was not likely
    # to be fixable in pure CSS, and asked Claude to take a look. It suggested
    # this imperative approach.
    #
    # The results were good, but not perfect. I manually fixed an issue with
    # extra spaces, for example: instead of `sibling.text`, Claude wanted to use
    # `' '.join(sibling.stripped_strings)`, which interacted strangely with
    # inline elements. Claude also didn't want to use := for some reason, which
    # I like because the code looks a bit cleaner.
    #
    # Overall I think the experiment was worthwhile, and yielded much better
    # behavior than what was here before. But at the end of this session, before
    # cleaning up the code, I made Claude give me the link to documentation it
    # referenced for `next_siblings` because I'd never used that before and
    # wanted to LEARN about it. I still prefer to write my own damn code. The
    # point of writing these side projects is the learning, just as much as the
    # "useful package" that I might create (or not).
    #
    # (There's some irony in how many AI-assisted autocomplete suggestions from
    # VS Code I had to ignore while writing this comment block about why I still
    # prefer to write things myself...)
    if (section_header := soup.select_one(f'[id="{section_id}" i]')) is None:
        return None

    paragraph_texts: list[str] = []
    for sibling in section_header.next_siblings:
        tag_name = getattr(sibling, 'name', None)

        # Stop when we hit the next heading.
        if tag_name in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            break

        if tag_name == 'p':
            if text := sibling.text:
                paragraph_texts.append(text)

    if not paragraph_texts:
        return None

    return ' '.join(paragraph_texts)


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
) -> dict[str, str]:
    """Search Know Your Meme by title keywords.

    :param query: The search keyword(s).
    :param user_agent: Optional custom user agent string to use in the headers.
    :return: A dictionary containing the title and URL of up to 10 results.

    This function uses the "quick links" endpoint from KYM's search bar. On the
    one hand, that isn't a public API, so it could break at any time. On the
    other hand… HTML scraping can break too, if the page structure changes.
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
            'len': 10,
        },
    )
    try:
        data = r.json()
    except ValueError:
        return {}

    return {
        item['name']: 'https://knowyourmeme.com' + item['url']
        for item in data['results']
    }
