# Drafts

Pages in this folder are not part of the live site yet.

- `pricing.html`: the CodexBar 2.0 pricing page (free tier, CodexBar Pro and its
  US prices). It must not go live before the CodexBar 2.0 price change
  ([#1](https://github.com/hemsoft-dev/codexbar-site/issues/1)).

How drafts stay private:

- `_redirects` sends every `/drafts/*` request to the home page on Cloudflare
  Pages. Cloudflare applies redirects before it serves files, so the draft is
  unreachable even though it is in the deployed tree.
- Each draft has `<meta name="robots" content="noindex, nofollow">`, and
  `robots.txt` disallows `/drafts/`.
- No live page links to a draft.

These protections rely on Cloudflare Pages. GitHub Pages ignores `_redirects`,
so a GitHub Pages deployment would serve `/drafts/pricing.html`.

To publish the pricing page after the 2.0 price change, in its own pull request:

1. Move `drafts/pricing.html` to `pricing/index.html`.
2. Remove the draft banner and the `robots` meta tag, and add
   `<link rel="canonical" href="https://codexbar.net/pricing/">`.
3. Add a Pricing link to the header and footer navigation on every page.
4. Recheck the prices and features against the shipped 2.0 App Store products.

Preview a draft locally at <http://localhost:8000/drafts/pricing.html> with the
command in the main README.
