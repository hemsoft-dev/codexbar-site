# codexbar-site

Source for [codexbar.net](https://codexbar.net): the product site, privacy
policy, terms and support page for CodexBar on every platform:

- iPhone, iPad and Apple Watch: [codexbar-ios](https://github.com/hemsoft-dev/codexbar-ios)
- Windows: [codexbar](https://github.com/hemsoft-dev/codexbar)
- macOS: [codexbar-mac](https://github.com/hemsoft-dev/codexbar-mac)

The site is plain HTML and one stylesheet. It has no build step, no
dependencies and no JavaScript. It loads nothing from other origins: no
analytics, cookies, trackers, web fonts or CDNs.

## Layout

| Path | Purpose |
| --- | --- |
| `index.html` | Home: features, providers, screenshots, platforms |
| `privacy/index.html` | Privacy policy, reproduced from `codexbar-ios/PRIVACY.md` |
| `terms/index.html` | Terms: Apple's standard EULA and each repository's license |
| `support/index.html` | Support, reproduced from `codexbar-ios/SUPPORT.md` |
| `404.html` | Not-found page (served automatically by Cloudflare Pages) |
| `assets/` | `site.css`, icons and screenshots |
| `_headers`, `_redirects`, `robots.txt` | Cloudflare Pages headers and redirects; crawler rules |
| `drafts/` | Pages that must not go live yet (see below) |
| `scripts/sync_ios_docs.py` | Copies the privacy policy and support text from `codexbar-ios` |

The header and footer markup is repeated in every page. Keep it identical when
you edit it. Pages link to each other with relative paths, except `404.html`,
which uses root paths because it is served at any URL.

## Local preview

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. The Python server doesn't serve `404.html`
for missing paths or apply `_headers` and `_redirects`; Cloudflare Pages does.

## Keeping the privacy policy and support page in sync

`codexbar-ios/PRIVACY.md` and `codexbar-ios/SUPPORT.md` are the sources of
truth. After either changes on `codexbar-ios` `main`, update this site in a pull
request:

```sh
git -C ../codexbar-ios pull
python3 scripts/sync_ios_docs.py ../codexbar-ios
```

The script rewrites only the text between the `BEGIN SYNC` and `END SYNC`
markers and records the source commit and its date at the top of each page.
It uses only the Python standard library.

## Deployment (Cloudflare Pages)

Connect this repository in the Cloudflare dashboard under **Workers & Pages >
Create > Pages > Connect to Git** with these settings:

- Production branch: `main`
- Framework preset: None
- Build command: none (leave empty)
- Build output directory: `/`

Every push to `main` then deploys automatically, and pull requests get preview
deployments. The Pages free plan covers this site, so the only recurring cost is
the domain.

### Pending for Franz

Connecting the repository and adding DNS need Franz's Cloudflare account. Do not
add Cloudflare credentials or tokens to this repository.

1. Create the Pages project from this repository with the settings above.
2. In the project's **Custom domains**, add `codexbar.net`. Cloudflare creates
   the DNS record and the TLS certificate because the zone is already on
   Cloudflare.
3. Add `www.codexbar.net` as a custom domain too, so it has a proxied DNS
   record. Then add a redirect rule in the zone (**Rules > Redirect Rules**)
   that sends requests for `www.codexbar.net` to `https://codexbar.net` with
   status 301, preserving the path and query string. `_redirects` can't
   redirect by host name.
4. Check: `curl -sI https://codexbar.net` returns 200 and
   `curl -sI https://www.codexbar.net` returns 301 to `https://codexbar.net/`.

After the site is live, update the App Store privacy, support and marketing
URLs through an issue in `codexbar-ios`.

GitHub Pages also works from the repository root, but it ignores `_headers` and
`_redirects`, so it would publish `drafts/`. Use Cloudflare Pages.

## Drafts and the pricing page

The pricing page must not go live before the CodexBar 2.0 price change. It is
kept in `drafts/pricing.html`, which no page links to, has a `noindex` tag, is
disallowed in `robots.txt` and is redirected away by `_redirects`. See
[drafts/README.md](drafts/README.md) for how to publish it.

## Content rules

- Keep copy plain and accurate. Don't invent features, numbers or testimonials.
- Label a platform that isn't released as coming soon, without a download link.
- Every image needs descriptive alt text. Check both light and dark appearance
  at phone and desktop widths before opening a pull request.
