# culturgen

`culturgen` is a Know Your Meme scraper.

It's originally based on an older scraper package called
`memedict` ([GitHub](https://github.com/Kraymer/memedict), [PyPI](https://pypi.org/project/memedict/)).

## Install

```sh
pip install culturgen
```

## Usage

Use `search()` to get a quick meme definition based on keywords:

```pycon
>>> import culturgen
>>> culturgen.search('all your base')
All Your Base Are Belong To Us. "All Your Base Are Belong to Us" is a popular
engrish catchphrase that grew popular across the internet as early as in 1998.
An awkward translation of "all of your bases are now under our control", the
quote originally appeared in the opening dialogue of Zero Wing, a 16-bit
shoot'em up game released in 1989. Marked by poor grammar, the "All Your Base"
phrase and the dialogue scene went viral on popular discussion forums in 2000,
spawning thousands of image macros and flash animations featuring the slogan
both on the web and in real life.
```

If you have a link to the Know Your Meme page (supports paths matching
`/memes/:slug` only), you can directly fetch information about that meme:

```pycon
>>> import culturgen
>>> culturgen.fetch('https://knowyourmeme.com/memes/mocking-spongebob')
Mocking SpongeBob. Mocking SpongeBob, also known as Spongemock, refers to an
image macro featuring cartoon character SpongeBob SquarePants in which people
use a picture of SpongeBob to indicate a mocking tone towards an opinion or
[...]
```

You can also do this with just the meme slug, handy for chat bot link handlers:

```pycon
>>> import culturgen
>>> culturgen.fetch('all-your-base-are-belong-to-us')
All Your Base Are Belong to Us. "All Your Base Are Belong to Us" is a popular
engrish catchphrase that grew popular across the internet as early as in 1998.
An awkward translation of "all of your bases are now under our control", the
[...]
```
