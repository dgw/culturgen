## Changelog

### 0.2.0

This version drops the development status back to "4 - Beta" because of some
experiments like changing how `search_meme()` fetches results.

Stick with `culturgen==0.1.0` if you want "`memedict`, but fixed, but not trying
new things yet". KYM site changes can always break stuff—it's the nature of HTML
scraping—but between here and 1.0.0 there will _also_ be library API changes,
and design/implementation missteps to correct.

* New `fetch()` function that works with a KYM page URL or slug
  * Useful if you already have the URL or slug, and more reliable than the old
    workaround (try to search for the slug with `-` replaced by ` `)
* The `search_meme()` function now calls the "quick links" backend that KYM's
  own search bar uses
  * Undocumented, of course, and subject to breaking (just like scraping HTML
    from the search result page was, to be fair)
* Extracted some lower-level logic into a `util` submodule (not considered
  public API; available functions and their behavior subject to change!)

### 0.1.1

* Made similarity threshold check case-insensitive

### 0.1.0

* Updated to fix apparent changes from KYM that broke the old library
* Modernized package metadata
* Made a few miscellaneous tweaks
