# Dragoș Iorgulescu — Personal Website & Engineering Journal

**Languages:** [Română](README.md) | [English](README.en.md)

Personal website completely migrated to a pure static architecture using **HTML5 / CSS / JavaScript**, **with zero dependencies on Hugo or any other static site generator**.

The site offers a carefully calibrated visual experience with two fully compatible design directions:
1. **Minimalist Editorial Design (Active / Current):** A calm, elegant, and fast layout focused on long-form reading across essays, technical guides, and training frameworks. Features a clean single-tier navbar (`h-16`), refined typography (`max-w-4xl`), breathable chronological lists, and subtle cards—eliminating HUD telemetry clutter while keeping the same core identity.
2. **Tactical Bento HUD Design (Complete Backup):** A dense technical interface inspired by sports telemetry dashboards (*Garmin Tactical*, *Whoop*, *Strava Dark*) and modern developer tools (*Linear*, *Raycast*), with a dual-tier HUD bar (`SYS // ONLINE`), live clock, and heavy Bento grid. Safely preserved 1:1 in `_backup_tactical_hud/`.

---

## ⚡ Technical Specifications

* **100% Pure HTML / Zero-Engine:** Every page is a standalone, self-contained HTML document that can be opened directly in any browser (`file://`) or deployed to any web server (Nginx, Apache, Caddy, GitHub Pages, Cloudflare Pages, etc.).
* **Dual Color Schemes (Dark & Light) with OS Auto-Detection:**
  * **Dark Mode (Obsidian Minimal):** Canvas `#0B0F17`, panels `#111827`, text `slate-300` / `slate-100`, calm Emerald accents (`#10B981`), optimized for extended reading.
  * **Light Mode (Technical Paper):** Clean `#F8FAFC` canvas, crisp `#FFFFFF` cards with subtle borders (`#E2E8F0`), high-contrast typography (WCAG AAA compliant), and zero glare.
  * **Intuitive Switcher (Desktop & Mobile):** Dedicated navbar toggle (Phosphor Icons Sun/Moon) with smooth transitions and zero FOUC.
  * **OS / Browser Auto-Detection:** Reads `prefers-color-scheme` on first visit and adapts dynamically if the user toggles their OS theme.
  * **Zero Flash of Wrong Theme (FOUC):** Synchronous inline script in `<head>` applies the theme before DOM rendering begins.
  * **Persistence via `localStorage`:** Remembers user preference across page navigations and browser sessions.
* **Frugal & 100% Autonomous Architecture (Zero External CDNs):**
  * **Zero Third-Party Requests:** Completely eliminated `cdn.tailwindcss.com`, `fonts.googleapis.com`, and `unpkg.com`. The site makes zero external requests, ensuring strict privacy and 100% offline capability (`file://` or air-gapped environments).
  * **Native High-Performance Typography:** Fast system font triad (`Space Grotesk`, `JetBrains Mono`, `Inter` with seamless OS fallbacks to `-apple-system`, `SF Mono`, `Segoe UI`, `Roboto`) eliminating layout shifts and network font lag (zero FOIT/FOUT).
  * **Pure CSS Autonomous Icons:** All Phosphor icons are embedded natively in `css/tactical.css` as GPU-accelerated SVG mask layers (zero external JavaScript libraries).
  * **Ultra-Lean Footprint:** Pages weigh under 30 KB total (a >99% bandwidth reduction compared to the previous Tailwind JIT runtime).
* **Instant Design Switching & Rollback:**
  * Revert to the dense **Tactical Bento HUD** anytime: `python3 restore_backup.py`
  * Recompile with the **Minimalist Editorial** design: `python3 publish.py --rebuild`

---

## 📂 File Structure

```
iorgos-hugo/
├── content/                     # Source Markdown content
│   ├── now.md                   # Source for the "Now" page (current focus)
│   ├── kettlebell.md            # Source for kettlebell & telemetry guide
│   ├── blog/                    # Source Markdown for journal essays
│   ├── howto/                   # Source Markdown for technical guides
│   └── programe/                # Source Markdown for training frameworks
├── programe/                    # Source templates for training frameworks
├── sounds/                      # Source template for audio archive & voidwave-lab
├── kettlebell/                  # Source template for kettlebell guide
├── images/                      # Media assets, diagrams, charts, and SVGs
├── css/                         # tactical.css (Dark Obsidian & Light Paper)
├── js/                          # tactical.js (Dark/Light controller, mobile menu)
├── public/                      # 🚀 COMPLETE GENERATED WEBSITE ROOT (ready to deploy)
│   ├── index.html               # Compiled homepage
│   ├── now.html                 # Compiled "Now" page
│   ├── sitemap.xml              # Generated sitemap XML for search engines
│   ├── robots.txt               # Crawler directives
│   ├── blog/                    # All compiled HTML essays
│   ├── howto/                   # All compiled HTML guides
│   ├── programe/                # All training program subpages
│   ├── sounds/                  # Compiled sounds page
│   ├── kettlebell/              # Compiled kettlebell protocol
│   ├── css/                     # Synchronized CSS styles
│   ├── js/                      # JavaScript assets
│   └── images/                  # Media assets & favicon
├── publish.py                   # Central CLI & generator (GPLv3)
├── restore_backup.py            # Instant restoration script to Tactical Bento HUD design
├── _backup_tactical_hud/        # Full untouched backup of the former Bento HUD design
├── build_tactical_site.py       # Standalone build utility
└── _legacy_hugo/                # Secure archive of former Hugo files & templates
```

---

## 🚀 How to View or Preview

### 1. Direct Viewing (Offline / Standalone)
Open `public/index.html` directly in any web browser via double-click. All internal links and images use relative paths calibrated to work without a web server.

### 2. Local Web Server
To launch a lightweight preview server (serving directly from `public/`):
```bash
# Using the built-in publish.py utility:
python3 publish.py --serve 8080

# Or via standard Python http.server from the public directory:
cd public && python3 -m http.server 8080
```
Then navigate to `http://localhost:8080`.

---

## ✍️ Content Publishing & Site Administration (`publish.py`)

To ingest new Markdown articles, delete older posts, scaffold drafts, or rebuild the entire site, use the zero-dependency **`publish.py`** utility:

### 📋 Command Cheat Sheet

| Action | Terminal Command | Description |
| :--- | :--- | :--- |
| **Publish new article** | `python3 publish.py article.md` | Auto-ingest to `content/`, compile HTML, and update indexes |
| **Force category** | `python3 publish.py article.md -c howto` | Directs publication to `blog`, `howto`, or `programe` |
| **Full site rebuild** | `python3 publish.py --rebuild` | Recompiles all HTML pages and purges orphaned directories |
| **Delete article** | `python3 publish.py --delete slug` | Removes `.md` source, deletes compiled HTML, updates indexes |
| **Scaffold new draft** | `python3 publish.py --new "Title" -c blog` | Generates a Markdown template with metadata headers |
| **Local preview server** | `python3 publish.py --serve 8080` | Starts local HTTP web server on port 8080 |

---

### 1. Adding a New Article from Markdown
Write your article in Markdown (e.g., `new-article.md`) and run:
```bash
python3 publish.py new-article.md
```
The script will:
* Detect the target category from the frontmatter (`category: blog`, `howto`, or `programe`).
* Copy the source Markdown into `content/<category>/<slug>.md`.
* Compile the standalone HTML page to `<category>/<slug>/index.html`.
* Reorder and update the category index archive (`<category>/index.html`).
* Update the main dashboard (`index.html`) refreshing recent dispatches and KPI counts.

To force a specific category from the command line:
```bash
python3 publish.py new-article.md --category howto
```

### 2. Deleting or Unpublishing an Article
To remove an article (for example, „compensare” under the blog category), choose one of three straightforward methods:

* **Option A — Direct CLI Command (Complete automated removal):**
  ```bash
  python3 publish.py --delete compensare
  # or using the category path:
  python3 publish.py --remove blog/compensare
  ```
  The script will:
  1. Remove the Markdown source: `content/blog/compensare.md`.
  2. Delete the compiled HTML directory: `blog/compensare/`.
  3. Automatically rebuild `blog/index.html` and `index.html`, decrementing the KPI dispatch counter.

* **Option B — Unpublish as Draft (preserves Markdown text):**
  Open `content/blog/compensare.md` and set:
  ```yaml
  draft: true
  ```
  Then run:
  ```bash
  python3 publish.py --rebuild
  ```
  The script removes the public HTML page from the site and indexes, but preserves your Markdown file in `content/blog/` for future republishing.

* **Option C — Manual Markdown Deletion:**
  If you manually delete `content/blog/compensare.md` and run:
  ```bash
  python3 publish.py --rebuild
  ```
  The script automatically detects orphaned HTML directories and cleans up `blog/compensare/`.

### 3. Rapid Full-Site Rebuild
Whenever you modify CSS styles in `css/tactical.css`, HTML templates, or multiple Markdown files in `content/`:
```bash
python3 publish.py --rebuild
# or simply:
python3 publish.py
```

### 4. Global Identity Configuration (Name, Subtitle, Channels)
To update your name, navbar subtitle (e.g. `Test Engineer · Strength Practitioner`), or communication channels, modify the `SITE_CONFIG` dictionary at the top of `publish.py`:
```python
SITE_CONFIG = {
    "author": "Dragoș Iorgulescu",
    "handle": "Dragoș Iorgulescu",
    "subtitle": "Test Engineer · Strength Practitioner",
    "location": "Bucharest, RO",
    "email": "dragos@iorgos.net",
    # ...
}
```
Then run:
```bash
python3 publish.py --rebuild
```
The script will propagate your updated identity across **all 25+ pages** across the entire website.

### 5. Generating a New Draft Template
To quickly scaffold a new article with all metadata fields pre-filled:
```bash
python3 publish.py --new "Configuring FreeBSD Suckless Tools" --category howto
```
This automatically generates `content/howto/configuring-freebsd-suckless-tools.md` ready for editing.

### 6. Recommended Frontmatter Header Structure
Every Markdown article accepts standard frontmatter:
```yaml
---
title: "Article or Technical Guide Title"
date: 2026-10-15
category: blog                 # "blog", "howto", or "programe" (default: blog)
slug: custom-article-slug      # optional (auto-generated from title if omitted)
tag: "LINUX // AUTOMATION"     # optional (auto-inferred if omitted)
badge_class: badge-emerald     # optional: badge-emerald, badge-sky, badge-amber, badge-purple
excerpt: "Short summary..."    # optional (auto-extracted from first paragraph)
read_time: "5 MIN READ"        # optional (auto-calculated from word count)
draft: false                   # optional (if true, excluded from public HTML)
---

# Section Header

Article content formatted in standard Markdown...
```

### 7. Switching or Restoring Design Styles

The repository maintains both design directions in fully working order:

* **To restore the previous Tactical Bento HUD design (with dual-tier HUD bar, live clock, and dense grid):**
  ```bash
  python3 restore_backup.py
  ```
  This script instantly restores original files from the safety archive `_backup_tactical_hud/`.

* **To recompile or switch back to the Minimalist Editorial design:**
  ```bash
  python3 publish.py --rebuild
  ```
  The `publish.py` engine rebuilds all essays, guides, and static pages with the clean, distraction-free reading layout.

---

## 📄 License

* **Generator Scripts & Tooling:** All Python site generation, publishing, and maintenance scripts (`publish.py`, `build_tactical_site.py`, `restore_backup.py`) are licensed under the **[GNU General Public License v3.0 (GPLv3)](LICENSE)**.
* **Content & Writings:** Original essays, technical articles, training guides, and media assets are &copy; 2026 Dragoș Iorgulescu (all rights reserved, unless stated otherwise).
