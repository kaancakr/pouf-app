# Pouf website

The public site for Pouf, the app that turns an iPhone into a touchpad, keyboard, media remote and app launcher for a Mac. It introduces the app, serves the Mac helper download, and holds the privacy policy and support page the App Store asks for. It is served by GitHub Pages at <https://kaancakr.github.io/pouf-app/>.

Plain HTML and one stylesheet: no build step, no JavaScript, no cookies, and nothing loaded from other sites.

## Addresses

| Page | English | Turkish |
| --- | --- | --- |
| Home | `/pouf-app/` | `/pouf-app/tr/` |
| Download | `/pouf-app/download/` | `/pouf-app/tr/download/` |
| Privacy policy | `/pouf-app/privacy/` | `/pouf-app/tr/privacy/` |
| Support | `/pouf-app/support/` | `/pouf-app/tr/support/` |

The iPhone app links to the download page, the privacy policy and the support email, so these addresses must not change once the app ships. If a custom domain is added later (Settings > Pages > Custom domain), GitHub redirects the `github.io` addresses to it. Links between pages are relative and keep working; the absolute `canonical`, `hreflang` and `og:` URLs in each page's `<head>` need the new domain.

## Layout

- `index.html`, `download/`, `privacy/`, `support/`: English pages. `tr/` holds the Turkish twin of each, at the same path.
- `assets/site.css`: the whole stylesheet. Colours, spacing and radii match the iPhone app's `PoufTheme`.
- `assets/icons.svg`: line icons, used as `<use href="…/icons.svg#name">`.
- `assets/pouf-mark.svg`: the logo, cropped to its drawing. `favicon.svg` is the uncropped mark from `Design/pouf-mark.svg` in the app's repository.
- The iPhone on the home page is drawn in HTML and CSS after the app's Remote tab, at the iPhone 17's 402 × 874 pt. If that tab's layout changes, update `.screen` in both home pages and in `site.css`.

## Check it

```sh
python3 -m http.server 8123
```

Open <http://localhost:8123/>. Before publishing, run:

```sh
python3 scripts/check_site.py
```

It fails if a link or image points to a missing file or icon, if a page has no twin in the other language, or if a page lacks `lang`, a title, a canonical link or its `hreflang` links.

## Release a new helper version

Releases in this repository are immutable (Settings > General > Releases > Enable release immutability): once a release is published, its DMG can't be replaced or deleted and its tag can't be moved, and GitHub attaches a signed attestation to it. A wrong upload therefore needs a new version number, not a replaced file.

1. Build the DMG in the app's repository with `Scripts/make-helper-dmg.sh` (see its README, "Releasing the helper").
2. Create the release as a draft with the DMG attached, check it on GitHub, then publish it:

   ```sh
   gh release create helper-v1.1 path/to/Pouf-Helper-1.1.dmg --repo kaancakr/pouf-app --title "Pouf Helper 1.1" --draft
   gh release edit helper-v1.1 --repo kaancakr/pouf-app --draft=false
   gh release verify-asset helper-v1.1 path/to/Pouf-Helper-1.1.dmg --repo kaancakr/pouf-app
   ```

3. In `download/index.html` and `tr/download/index.html`, update the download link, the version, the size, and the file name in the first install step and in the command under "Checking the download". If the signing team ever changes, update the Team ID in the card and in that section too.

The pages don't show a SHA-256: it would sit beside the file it describes, so anyone able to swap the file could change it too. The signature check and the release attestation are the checks that hold.

## Security

- The DMG and the app inside it are signed with Developer ID (Team ID `K768X7CB7V`) and notarized. That signature, checked by Gatekeeper, is what protects users from a tampered download; the download page shows how to check it.
- Every page sets a Content Security Policy in a `<meta>` tag (GitHub Pages can't send custom headers): no scripts, and styles and images only from this site. A page that needs anything else must widen that policy on purpose.

## Before the iPhone app ships

- The support address is the placeholder `support@example.com` on the privacy and support pages, in both languages.
- The App Store button reads "coming soon" and the second setup step says the app is coming. Replace both with the App Store link once the app has one.
