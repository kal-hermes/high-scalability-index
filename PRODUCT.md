# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Delegated. No-build static SPA (plain HTML/CSS/JS, no framework). Chosen because the deploy
target is GitHub Pages, which serves static files only. It also matches the ksze.github.io
workflow and needs no build toolchain in the container. Static files deploy to a GitHub
Pages site under the kal-hermes GitHub account.

## Users

Primary user: public visitors on the internet. These are engineers and architects who want
to find scalability articles by topic instead of by chronology. The site is fully public.
Any person with the URL can browse it.
Owner/maintainer: k_sze, who curates the underlying dataset and deploys updates.

## Product Purpose

A public, topic-organized catalogue of the HighScalability.com article archive. It covers
2,451 articles (2007 to 2024) classified into 27 topics. An article can belong to several
topics. Visitors search and filter by topic, scan titles with dates and authors, and click
through to the original articles on highscalability.com. Success means a visitor can find
every article on a subject in seconds. Examples: Kafka, caching, war stories. No more
paging through 205 archive pages.

## Positioning

HighScalability.com itself offers only reverse-chronological pagination and no topic index.
This catalogue is the only public, multi-topic, machine-verified index of the full archive.
It was built from every article's full text plus the site's own editorial tags.

## Operating Context

- Python scripts in this repo generate the dataset (fetch, parse, classify, verify) from
  the raw HTML archive. The UI consumes the generated JSON and never the live site.
- Local dev and verification: files are served by a host-side HTTP server because the
  container cannot bind host-reachable ports. Rendered verification runs through the
  Camofox browser tier.
- Deployment: a static file push to GitHub Pages. No server-side code and no API.

## Capabilities and Constraints

- Data source of truth: `articles_v2.json` with url, title, excerpt, author, date,
  site_tags, topics, and first-seen page. It holds about 2,451 records. Client-side
  filter and search run on a loaded JSON payload of roughly 1 MB. That is acceptable.
  There is no backend.
- Topics are multi-label by design. An article can appear under several topics.
- Copyright: HighScalability articles belong to their authors. The site indexes and links
  to the originals with short excerpts only. It must never republish full article text.
- Recurring content-type buckets exist beside the technical topics: Link Roundups (468),
  Sponsored Posts (268), Papers and Books & Research, and Company Profiles & War Stories.
- Deploy target is GitHub Pages. Use relative asset paths, no server rewrites, and no
  dynamic routes.

## Brand Commitments

None established. Naming and placement (repo name, GitHub Pages project path) are undecided.

## Evidence on Hand

- `articles_v2.json` is the verified dataset (2451 articles, 27 topics, site tags).
- `CATALOGUE.md` and `INDEX.md` are the human-readable outputs and the count parity
  reference.
- `classification_changes.json` is the audit trail of classification decisions.
- `articles_html/` holds the raw archived pages (local only, not for deployment).
- Absence to preserve: no full-text article content ships publicly because of copyright.

## Product Principles

1. Findability beats a false show of completeness. Every article is reachable by topic
   within seconds.
2. Index, do not republish. Link out to originals and keep excerpts short.
3. Data is generated, not hand-edited. The UI never forks from `articles_v2.json`.
4. Zero backend. Everything is static and all filtering and search happen client-side.

## Accessibility & Inclusion

No product-specific requirement was established. Standard web accessibility applies as the
default floor: WCAG AA contrast, keyboard operability, and reduced-motion support.
