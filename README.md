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
