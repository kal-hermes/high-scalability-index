---
name: The High Scalability Index
description: A back-issue newspaper archive browser for 2,451 highscalability.com articles.
colors:
  ground: "#f6f2e9"
  paper: "#f5f0e2"
  ink: "#171512"
  ink-soft: "#45403a"
  red: "#5e0e0e"
  tint: "rgba(255, 253, 245, .55)"
  hair: "rgba(23, 21, 18, .28)"
  hair-strong: "rgba(23, 21, 18, .55)"
  depth-1: "#efece0"
  depth-2: "#e3ddc9"
  depth-3: "#d3ccb2"
  depth-4: "#c0b692"
  depth-5: "#a89a67"
typography:
  display:
    fontFamily: "Anton, New Amsterdam, sans-serif"
    fontSize: "5.7vw"
    fontWeight: 400
    lineHeight: 0.95
    letterSpacing: "0em"
  headline:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1.5vw"
    fontWeight: 700
  label:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1.05vw"
    fontWeight: 700
    letterSpacing: "0.05em"
  body:
    fontFamily: "Source Serif 4, Georgia, Times New Roman, serif"
    fontWeight: 400
    lineHeight: 1.45
  accent-serif:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontStyle: italic
    fontWeight: 600
    fontSize: "1.3vw"
  mark:
    fontFamily: "Rokkitt, serif"
    fontSize: "0.8vw"
    fontWeight: 700
  dateline:
    fontFamily: "Oswald, sans-serif"
    fontSize: "1.462vw"
    fontWeight: 500
    letterSpacing: "0.02em"
rounded:
  none: "0"
spacing:
  xs: "0.5vw"
  sm: "1vw"
  md: "2vw"
  lg: "3vw"
  xl: "4.6vw"
components:
  rail-link:
    textColor: "{colors.ink}"
    typography: "{typography.headline}"
    padding: "1.1vw 8px 1.1vw 2px"
  count-badge:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.mark}"
    padding: "0.1vw 0.5vw"
  count-badge-active:
    backgroundColor: "{colors.red}"
    textColor: "{colors.paper}"
  marker-bar:
    backgroundColor: "{colors.red}"
    size: "0.7vw"
---

# Design System: The High Scalability Index

## Overview

**Creative North Star: "The Back-Issue Index"**

The page is a newspaper archive you leaf through. Newsprint ivory ground, engraving ink, hairline rules. One deep signal red owns the masthead rules, the kickers, and the count marks. Everything else is ink on paper.

The layout is a broadsheet. A sections rail sits on the left with a hairline rule between rail and page. A thick-thin double rule signs the dateline band under the masthead. Article rows read like classified listings. Expanding a row reveals a broadsheet abstract in italic serif.

Type sizes are vw-locked to the approved comp frame (2736 by 1536). This keeps the archive scale-stable at every capture width.

**Key Characteristics:**
- Newsprint ground with fiber grain in the lower folio
- Hairline rules everywhere. The thick-thin dateline is the only heavy signature
- One signal red at low area share
- Condensed caps for wayfinding, serif for reading
- Count badges as small print marks

## Colors

The palette is ivory paper, two inks, and one deep red. Five depth steps rank section depth.

### Primary
- **Engraving Ink** (#171512): All text, rules, badges, and the grain dots. Near black with warm brown bias.

### Secondary
- **Signal Red** (#5e0e0e): Masthead rules, kickers, active markers, active badges. Dark oxblood, never bright. Keep its area share small.

### Neutral
- **Newsprint Ground** (#f6f2e9): Page background and html base.
- **Paper** (#f5f0e2): Panel fills, badge text, input fields.
- **Soft Ink** (#45403a): Secondary text, hover thumb on the scrollbar.
- **Hairlines** (rgba(23, 21, 18, .28) and .55): All rules. The strong step signs the rail heading and dateline.
- Depth steps 1 to 5 rank section coverage: #efece0 to #a89a67. Darker means deeper coverage.

## Typography

**Display Font:** Anton, with New Amsterdam fallback.
**Body Font:** Source Serif 4, with Georgia fallback.
**Wayfinding Fonts:** Archivo bold, Oswald.
**Mark Font:** Rokkitt.

**Character:** A news face for labels and a book serif for reading. Display is a single heavy condensed gothic voice. Labels are condensed bold caps with tight tracking.

### Hierarchy
- **Display** (Anton 400, 5.7vw, line-height .95): The masthead title only.
- **Headline** (Archivo 700, 1.5vw): Rail section links and row titles.
- **Label** (Archivo 700, 1.05vw, tracking .05em, uppercase): The SECTIONS heading.
- **Kicker** (Oswald 500, 0.8vw, tracking .2em, uppercase): Section kickers in signal red.
- **Body** (Source Serif 4 400, line-height 1.45): Row excerpts and colophon.
- **Accent serif** (Source Serif 4 italic 600, 1.3vw): Standfirst and tagline. Excerpts at 1.58vw.
- **Mark** (Rokkitt 700, 0.8vw): Numerals inside count badges.
- **Dateline** (Oswald 500, 1.462vw, tracking .02em, uppercase): The volume counts line in the dateline band.

### Named Rules
**The Two Voices Rule.** Sans condensed caps navigate. Serif reads. Never swap their roles.

## Layout

A broadsheet grid: sections rail on the left, page flow on the right. The rail column is 24 percent wide with a hairline right rule. The rail holds the SECTIONS label, the 27 section links with count badges, and a red marker bar on the active section.

The dateline band sits under the masthead. Volume counts on the left, search on the right, thick-thin rules under both. The page column stacks section head, filter chips, standfirst, listing rows, continued line, pager, and colophon.

Spacing rhythm runs on vw steps: 0.5vw, 1vw, 2vw. The type scale is vw-locked to the comp frame. Mobile (390px) rescales display sizes: section titles 6.4vw, row titles 4.6vw, both with overflow-wrap anywhere.

## Elevation & Depth

No shadows. Depth comes from the newsprint ground plate, the fiber grain overlay, and hairline rules. The depth color scale (five steps) ranks section coverage without elevation.

## Shapes

Everything is square. Zero radius on badges, inputs, chips, and rules. Corners stay sharp like printed matter. Rules are 1px hairlines except the two heavy signatures: the 6px section-head top rule and the 3px dateline rule with its thin companion.

## Components

### Masthead
- The title in Anton at 5.7vw, centered, with a slight text stroke to match comp weight.
- Kicker line above in Oswald caps, signal red.

### Dateline Band
- Volume counts left, search right, on one band under the masthead.
- Thick-thin rule signature below. Search input square, paper fill, hairline border.

### Sections Rail
- SECTIONS label in Archivo caps over a strong hairline.
- Links in Archivo 700 with Rokkitt count badges on ink squares.
- Active row: red marker bar on the left, red badge, no tint fill.
- Rail scrolls independently at 46vh max height.

### Listing Rows (signature component)
- Compact rows: title, date, author on one line with hairline separators.
- Click expands into a broadsheet abstract in italic serif with a 240ms reveal.
- Hover turns the title signal red.
- Honors prefers-reduced-motion: the reveal collapses to an instant swap.

### Filter Chips
- Oswald caps, 0.08em tracking, paper fill, hairline border, square.

### Pager and Colophon
- Pager buttons square with hairline borders.
- Colophon in body serif under a hairline, inside the ground.

## Do's and Don'ts

### Do:
- Do keep all type sizes in vw units locked to the comp frame.
- Do keep fonts self-hosted with font-display block.
- Do use the strong hairline (rgba .55) for signatures and the light one (.28) everywhere else.
- Do verify tone and geometry against the comp with RGB pixel samples and rect probes.

### Do not:
- **Do not** add shadows or rounded corners.
- **Do not** brighten the signal red or raise its area share.
- **Do not** leave scrollbars at native styling. Keep the thin palette scrollbar.
- **Do not** let labels and reading type swap voices.
