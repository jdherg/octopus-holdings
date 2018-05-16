# 🐙

Octopus Holdings is a website that translates a series of tokens (provided via the URL) into an emoji composition.

## 📝

Octopus Holdings compositions are defined by a series of tokens in the URL that follow the domain (`octopus.holdings(/token)*`).

Octopus Holdings will likely always support the basic syntax `(/alias)*` where each `alias` is some alias for an emoji (like an emoji itself, one of the aliases that [gemoji](https://github.com/github/gemoji) lists for it, or the hex codepoints joined by `-`). It renders as a stack of emoji corresponding to those aliases. A single alias alone (`/foo` ) is rendered with an octopus (equivalent to `/foo/octopus`) and no alias at all is rendered as a default emoji on top of the octopus (equivalent to `/foo/octopus` if `foo` is an alias for the default emoji). A token that isn't recognized by the website is rendered as ❓.

### 🔀

There is one stabilized non-alias token: `random` will be rendered as a randomly selected emoji.

### 🔬

There are also experimental non-alias tokens. Syntax for these tokens hasn't specialized and URLs using them may be less likely to work in the future.

The first set of experimental tokens vary the emoji set that's used to render all of the aliases that follow them (up to the next emoji set token or. There are currently four supported emoji sets: `noto_1`, `noto_2`, `twemoji_2_6_0`, and `fxemoji`. For example, `/noto_1/octopus/noto_2/octopus/twemoji_2_6_0/octopus/fxemoji/octopus` is the octopus emoji as depicted in each of the four variants.

## ⚖️

Details on third-party code/assets can be found in third_party.
