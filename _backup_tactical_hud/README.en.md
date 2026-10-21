# Dragoș Iorgulescu — Personal Website & Tactical HUD

**Languages:** [Română](README.md) | [English](README.en.md)

Personal website completely migrated to a pure static architecture using **HTML5 / CSS / JavaScript**, **with zero dependencies on Hugo or any other static site generator**.

The visual design system applied is **"Tactical Dark / Bento HUD"**, inspired by technical sports interfaces (*Garmin Tactical*, *Whoop*, *Strava Dark*) and modern developer design aesthetics (*Linear*, *Raycast*).

---

## ⚡ Technical Specifications

* **100% Pure HTML / Zero-Engine:** Every page is a standalone, self-contained HTML document that can be opened directly in any browser (`file://`) or deployed to any web server (Nginx, Apache, Caddy, GitHub Pages, Cloudflare Pages, etc.).
* **Dual Color Schemes (Dark & Light) with OS Auto-Detection:**
  * **Dark Mode (Tactical Dark — default):** `#0B0F17` canvas, `#111827` Bento panels with backdrop blur, neon accents, and status indicators.
  * **Light Mode (Technical Paper / Lab HUD):** Clean `#F8FAFC` canvas, crisp `#FFFFFF` panels with subtle elevation shadows, high-contrast `#0F172A` / `#334155` typography (WCAG AAA compliant), lab accents, and zero glare.
  * **Intuitive Switcher (Desktop & Mobile):** Dedicated navbar toggle (Phosphor Icons Sun/Moon) with real-time feedback in the top HUD bar (`MODE // DARK` / `MODE // LIGHT`).
  * **OS / Browser Auto-Detection:** Reads `prefers-color-scheme` on first visit and adapts dynamically if the user toggles their OS theme.
  * **Zero Flash of Wrong Theme (FOUC):** Synchronous inline script in `<head>` applies the theme before DOM rendering begins.
  * **Persistence via `localStorage`:** Remembers user preference across page navigations and browser sessions.
* **Tactical Dark / Bento HUD Design System:**
  * **Canvas:** `#0B0F17` (Dark) / `#F8FAFC` (Light)
  * **Bento Panels:** `#111827` at 88% opacity + `backdrop-filter: blur(12px)` (Dark) / `#FFFFFF` with precision drop shadows (Light)
  * **Recessed Containers:** Technical insets with subtle `1px` borders (`#1E293B` / `#CBD5E1`)
  * **Soft Glow Badges:** Semantic accents on tinted backgrounds (Emerald `#10B981`, Amber `#F59E0B`, Purple `#A855F7`, Sky `#38BDF8`)
  * **Typography Triad (Google Fonts):**
    1. `Space Grotesk` (Headlines, brand handles, technical separators `//`)
    2. `JetBrains Mono` (Metrics, dates, counts, categories, live clock)
    3. `Inter` (Body prose, descriptions, technical guides)
  * **Phosphor Icons:** `@phosphor-icons/web` (`ph-duotone` and `ph-bold`)
  * **Status Pills:** Live HUD indicators with pulsing beacon (`w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse`).

---

## 📂 File Structure

```
iorgos-hugo/
├── index.html                   # Main Tactical Bento HUD Dashboard
├── now.html                     # "Now" Page (real-time focus & active projects)
├── blog/
│   ├── index.html               # Journal / Essay archive with live client search
│   ├── telefonul/               # Essay: The Smartphone
│   ├── pacaneaua-din-buzunar/   # Essay: The Pocket Slot Machine
│   ├── curatenie-reprezentata-femei/
│   ├── soferi-grabiti-scaune-copii/
│   ├── compensare/
│   ├── tool-becomes-drug/
│   ├── gasit-nordul/
│   └── is-strava-another-facebook/
├── programe/
│   ├── index.html               # Bento Training Hub for physical conditioning
│   ├── tension-spectrum/        # Tension Spectrum Protocol + SVG diagrams
│   ├── sfg-prep/                # 3-Phase SFG I & SFB preparation framework
│   └── bjj-prep/                # BJJ elbow rehabilitation & aerobic base
├── howto/
│   ├── index.html               # Technical How-To archive with live client search
│   ├── deploy-hyperv2019/       # Guide: Workgroup Hyper-V Server Deployment
│   ├── create-fixed-size-files/ # Guide: Preallocated Dummy Files
│   ├── aliases-profiles-pwsh/   # Guide: PowerShell Profiles & Aliases
│   ├── ssh-auth-windows10/      # Guide: SSH Key Authentication on Windows 10
│   ├── first-homelab/           # Guide: First Homelab (Supermicro, Proxmox)
│   ├── first-raspberrypi-cluster/# Guide: Raspberry Pi 4 k3s Cluster
│   └── compiling-suckless-tools-freebsd/ # Guide: Compiling dwm/dmenu on FreeBSD
├── kettlebell/
│   └── index.html               # Navy Seal Burpees & Hardstyle Protocol
├── sounds/
│   └── index.html               # Audio archive (Scentient Pencils, Sentem, etc.)
├── images/                      # Media assets, diagrams, charts, and SVGs
├── css/
│   └── tactical.css             # Dual-theme Tactical Design System
├── js/
│   └── tactical.js              # Theme controller (Dark/Light), live clock, copy code
├── publish.py                   # Central CLI: Ingest Markdown, Rebuild, Delete, Drafts, Serve
├── build_tactical_site.py       # Standalone build utility
└── _legacy_hugo/                # Secure archive of former Hugo files & templates
```

---

## 🚀 How to View or Preview

### 1. Direct Viewing (Offline / Standalone)
Open `index.html` directly in any web browser via double-click. All internal links and images use relative paths calibrated to work without a web server.

### 2. Local Web Server
To launch a lightweight preview server:
```bash
# Using the built-in publish.py utility:
python3 publish.py --serve 8080

# Or via standard Python http.server:
python3 -m http.server 8080
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
To update your name, navbar subtitle (e.g. `TEST ENGINEER // STRENGTH PRACTITIONER // ASPIRING VIDEOGRAPHER`), or communication channels, modify the `SITE_CONFIG` dictionary at the top of `publish.py`:
```python
SITE_CONFIG = {
    "author": "Dragoș Iorgulescu",
    "handle": "// DRAGOȘ IORGULESCU",
    "subtitle": "TEST ENGINEER // STRENGTH PRACTITIONER // ASPIRING VIDEOGRAPHER",
    "location": "BASE // BUCHAREST, RO",
    "email": "dragos@iorgos.net",
    ...
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
