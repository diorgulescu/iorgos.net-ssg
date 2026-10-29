#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TACTICAL DARK // SITE PUBLISHER & GENERATOR
Dragoș Iorgulescu - Standalone Zero-Dependency Publishing System
=============================================================================
Copyright (C) 2026 Dragoș Iorgulescu <dragos@iorgos.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
=============================================================================

Usage:
  1. Publish/Ingest a new Markdown file:
       python3 publish.py cale/catre/articol-nou.md
       python3 publish.py articol-nou.md --category howto

  2. Rebuild the entire site from content/ directory:
       python3 publish.py --rebuild
       # or simply:
       python3 publish.py

  3. Create a new article draft template:
       python3 publish.py --new "Titlul Articolului" --category blog

  4. Start local preview server:
       python3 publish.py --serve 8080
"""

import sys, os, re, html, math, shutil, argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "public"

# =============================================================================
# SITE GLOBAL CONFIGURATION
# Configurare centralizată: modifică aici titlul, subtitlul, autorul etc.
# Modificările de aici se propagă automat pe toate paginile la rularea scriptului.
# =============================================================================
SITE_CONFIG = {
    "author": "Dragoș Iorgulescu",
    "handle": "Dragoș Iorgulescu",
    "subtitle": "Test Engineer · Strength Practitioner",
    "location": "Bucharest, RO",
    "site_title_suffix": "Dragoș Iorgulescu",
    "site_url": "https://iorgos.net",
    "email": "dragos@iorgos.net",
    "mastodon": "https://mastodon.social/@diorgulescu",
    "github": "https://github.com/diorgulescu",
    "youtube": "https://www.youtube.com/@iorgosnet",
}

# --- Month Formatting ---
MONTHS = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
}

def format_display_date(iso_date):
    parts = str(iso_date).strip().split('-')
    if len(parts) == 3:
        y, m, d = parts
        month_name = MONTHS.get(m, m)
        try:
            day_int = int(d)
            return f"{day_int:02d} {month_name} {y}"
        except ValueError:
            return f"{d} {month_name} {y}"
    return str(iso_date)

def slugify(text):
    text = text.lower()
    replacements = {
        'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ş': 's', 'ț': 't', 'ţ': 't',
        'é': 'e', 'è': 'e', 'ó': 'o', 'ö': 'o', 'ü': 'u', 'ä': 'a'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^a-z0-9\-]+', '-', text)
    return text.strip('-')

# --- Built-in Zero-Dependency Markdown Parser ---
def inline_format(text):
    # Inline code
    text = re.sub(r'`([^`]+)`', lambda m: f'<code>{html.escape(m.group(1))}</code>', text)
    # Images: ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Bold italic: ***text***
    text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold: **text** or __text__
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
    # Italic: *text* or _text_
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<em>\1</em>', text)
    # Strikethrough
    text = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', text)
    return text

def parse_markdown(raw_content):
    meta = {}
    body = raw_content

    # Frontmatter detection
    if raw_content.startswith('---'):
        parts = raw_content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            for line in fm_text.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    k, v = line.split(':', 1)
                    k = k.strip().lower()
                    v = v.strip().strip('"').strip("'")
                    meta[k] = v

    # 1. Extract code blocks with triple backticks
    code_blocks = []
    def save_code(m):
        lang = m.group(1).strip()
        code = m.group(2)
        idx = len(code_blocks)
        cls = f' class="language-{lang}"' if lang else ''
        code_blocks.append(f'<pre><code{cls}>{html.escape(code.strip())}</code></pre>')
        return f'\n\n@@@CODE_BLOCK_{idx}@@@\n\n'

    body = re.sub(r'```(\w*)\n(.*?)```', save_code, body, flags=re.DOTALL)

    # 2. Extract raw HTML blocks (divs, tables, sections, styles, posters)
    html_blocks = []
    def save_html(m):
        idx = len(html_blocks)
        html_blocks.append(m.group(0))
        return f'\n\n@@@HTML_BLOCK_{idx}@@@\n\n'

    body = re.sub(r'<(div|section|table|style|p\s+align)[^>]*>.*?</\1>', save_html, body, flags=re.DOTALL | re.IGNORECASE)

    # 3. Process blocks
    blocks = body.split('\n\n')
    out_blocks = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Check placeholders
        if block.startswith('@@@CODE_BLOCK_') and block.endswith('@@@'):
            idx = int(block.replace('@@@CODE_BLOCK_', '').replace('@@@', ''))
            out_blocks.append(code_blocks[idx])
            continue

        if block.startswith('@@@HTML_BLOCK_') and block.endswith('@@@'):
            idx = int(block.replace('@@@HTML_BLOCK_', '').replace('@@@', ''))
            out_blocks.append(html_blocks[idx])
            continue

        # Headers
        h_m = re.match(r'^(#{1,6})\s+(.*)$', block)
        if h_m:
            lvl = len(h_m.group(1))
            h_text = inline_format(h_m.group(2).strip())
            h_id = re.sub(r'[^a-zA-Z0-9\-]+', '-', h_m.group(2).strip().lower()).strip('-')
            out_blocks.append(f'<h{lvl} id="{h_id}">{h_text}</h{lvl}>')
            continue

        # Horizontal rule
        if re.match(r'^(?:---|\*\*\*|___)$', block):
            out_blocks.append('<hr class="separator" />')
            continue

        # Blockquote
        if block.startswith('>'):
            q_lines = [l.lstrip('> ').strip() for l in block.split('\n')]
            q_text = inline_format(' '.join(q_lines))
            out_blocks.append(f'<blockquote><p>{q_text}</p></blockquote>')
            continue

        # Unordered list
        if any(block.startswith(p) for p in ('- ', '* ', '+ ')):
            items = []
            for line in block.split('\n'):
                line = line.strip()
                m = re.match(r'^[-*+]\s+(.*)$', line)
                if m:
                    items.append(f'<li>{inline_format(m.group(1))}</li>')
            out_blocks.append(f'<ul>\n{"".join(items)}\n</ul>')
            continue

        # Ordered list
        if re.match(r'^\d+\.\s+', block):
            items = []
            for line in block.split('\n'):
                line = line.strip()
                m = re.match(r'^\d+\.\s+(.*)$', line)
                if m:
                    items.append(f'<li>{inline_format(m.group(1))}</li>')
            out_blocks.append(f'<ol>\n{"".join(items)}\n</ol>')
            continue

        # Markdown Table: | col1 | col2 |
        if block.startswith('|') and '|' in block[1:]:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if len(lines) >= 2 and re.match(r'^\|?[\s\-:|]+\|?$', lines[1]):
                headers = [inline_format(c.strip()) for c in lines[0].strip('|').split('|')]
                th_html = ''.join(f'<th>{c}</th>' for c in headers)
                rows_html = []
                for row_line in lines[2:]:
                    cells = [inline_format(c.strip()) for c in row_line.strip('|').split('|')]
                    td_html = ''.join(f'<td>{c}</td>' for c in cells)
                    rows_html.append(f'<tr>{td_html}</tr>')
                out_blocks.append(f'<table>\n<thead><tr>{th_html}</tr></thead>\n<tbody>\n{"".join(rows_html)}\n</tbody>\n</table>')
                continue

        # Paragraph
        p_text = inline_format(block.replace('\n', ' '))
        out_blocks.append(f'<p>{p_text}</p>')

    rendered_html = '\n\n'.join(out_blocks)
    return meta, rendered_html, body

def clean_content_paths(content_html, depth=0):
    root_path = "./" if depth == 0 else "../" * depth
    # rewrite root /images/ to relative {root_path}images/
    cleaned = re.sub(r'src=["\']/images/(.*?)["\']', f'src="{root_path}images/\\1"', content_html)
    cleaned = re.sub(r'href=["\']/images/(.*?)["\']', f'href="{root_path}images/\\1"', cleaned)
    cleaned = re.sub(r'href=["\']/docs/(.*?)["\']', f'href="{root_path}docs/\\1"', cleaned)
    return cleaned

# --- HTML Master Templates ---
def get_html_head(title, depth=0):
    root_path = "./" if depth == 0 else "../" * depth
    clean_title = title.strip()
    author = SITE_CONFIG.get("author", "Dragoș Iorgulescu")
    if author not in clean_title:
        page_title = f"{clean_title} // {author}"
    else:
        page_title = clean_title

    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="Personal website, training frameworks, technical how-tos, and audio archives by Dragoș Iorgulescu.">
  
  <link rel="icon" type="image/x-icon" href="{root_path}images/favicon.ico">
  <link rel="sitemap" type="application/xml" title="Sitemap" href="{root_path}sitemap.xml">
  <link rel="alternate" type="application/rss+xml" title="RSS Feed" href="{root_path}feed.xml">
  
  <!-- Zero-FOUC Theme Initializer: detects saved preference or OS system theme -->
  <script>
    (function() {{
      var stored = localStorage.getItem('theme_preference');
      var theme = stored || (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
      document.documentElement.classList.remove('dark', 'light');
      document.documentElement.classList.add(theme);
      document.documentElement.setAttribute('data-theme', theme);
    }})();
  </script>

  <!-- Frugal Tactical Design System (100% Autonomous / Zero External CDNs) -->
  <link rel="stylesheet" href="{root_path}css/tactical.css">
</head>
<body class="bg-[#0B0F17] text-slate-300 font-sans antialiased selection:bg-emerald-500/30 selection:text-white">
"""

def get_header(active_nav="", depth=0):
    root_path = "./" if depth == 0 else "../" * depth
    
    def active_cls(nav_name):
        if nav_name == active_nav:
            return "text-slate-100 font-semibold"
        return "text-slate-400 hover:text-slate-100 transition-colors"

    now_active = "text-slate-100 font-semibold" if active_nav == "now" else "text-slate-400 hover:text-slate-100 transition-colors"

    return f"""  <!-- CLEAN EDITORIAL NAVBAR -->
  <header class="sticky top-0 z-50 backdrop-blur-md bg-[#0B0F17]/90 border-b border-slate-800">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
      <a href="{root_path}" class="flex items-center gap-2 group">
        <span class="font-display font-bold text-slate-100 text-base tracking-tight hover:text-amber-400 transition-colors">
          Dragoș Iorgulescu
        </span>
      </a>

      <!-- Desktop Nav -->
      <nav class="hidden md:flex items-center gap-6 font-mono text-xs">
        <a href="{root_path}blog/" class="{active_cls('blog')}">Journal</a>
        <a href="{root_path}programe/" class="{active_cls('programe')}">Programs</a>
        <a href="{root_path}sounds/" class="{active_cls('sounds')}">Sounds</a>
        <a href="{root_path}howto/" class="{active_cls('howto')}">How-To</a>
        <a href="{root_path}now.html" class="inline-flex items-center gap-1.5 {now_active}">
          <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          Now
        </a>
        <a href="{root_path}feed.xml" class="text-slate-400 hover:text-orange-400 transition-colors" title="RSS Feed">
          <span class="font-mono text-sm">📡</span>
        </a>

        <!-- Minimal Theme Toggle Button -->
        <button type="button" class="theme-toggle-btn ml-2 p-1.5 rounded text-slate-400 hover:text-slate-100 transition-colors cursor-pointer" title="Toggle Theme" aria-label="Toggle Theme">
          <span class="theme-toggle-icon font-mono text-sm leading-none">☼</span>
        </button>
      </nav>

      <!-- Mobile Menu Button & Toggle -->
      <div class="flex items-center gap-2 md:hidden">
        <button type="button" class="theme-toggle-btn p-2 rounded text-slate-400 hover:text-slate-100 cursor-pointer" aria-label="Toggle Theme">
          <span class="theme-toggle-icon font-mono text-sm leading-none">☼</span>
        </button>
        <button id="mobile-menu-btn" class="p-2 rounded text-slate-400 hover:text-white font-mono text-xs" aria-label="Menu">
          <span>menu</span>
        </button>
      </div>
    </div>

    <!-- Mobile Dropdown -->
    <div id="mobile-menu" class="hidden md:hidden border-t border-slate-800 bg-[#0B0F17]/98 px-4 py-4 space-y-3 font-mono text-xs">
      <a href="{root_path}" class="block text-slate-300 hover:text-white">Home</a>
      <a href="{root_path}blog/" class="block text-slate-300 hover:text-white">Journal</a>
      <a href="{root_path}programe/" class="block text-slate-300 hover:text-white">Training Programs</a>
      <a href="{root_path}sounds/" class="block text-slate-300 hover:text-white">Sounds</a>
      <a href="{root_path}howto/" class="block text-slate-300 hover:text-white">How-To</a>
      <a href="{root_path}now.html" class="block text-amber-400 font-semibold">Now</a>
      <a href="{root_path}feed.xml" class="block text-orange-400 hover:text-orange-300">RSS Feed</a>
    </div>
  </header>
"""

def get_footer(depth=0):
    root_path = "./" if depth == 0 else "../" * depth
    return f"""  <!-- MINIMAL FOOTER -->
  <footer class="mt-20 border-t border-slate-800 py-12 px-4 sm:px-6">
    <div class="max-w-4xl mx-auto space-y-4 font-mono text-xs text-slate-400">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span class="font-bold text-slate-200 text-sm">Dragoș Iorgulescu</span>
          <span class="text-slate-500 block sm:inline sm:ml-2">&middot; Lift heavy. Be kind. Build robust software.</span>
        </div>
        <div class="flex items-center gap-4 text-slate-400">
          <a href="mailto:dragos@iorgos.net" class="hover:text-slate-200 transition-colors">Email</a>
          <a rel="me" href="https://mastodon.social/@diorgulescu" target="_blank" class="hover:text-slate-200 transition-colors">Mastodon</a>
          <a href="https://github.com/diorgulescu" target="_blank" class="hover:text-slate-200 transition-colors">GitHub</a>
          <a href="https://www.youtube.com/@iorgosnet" target="_blank" class="hover:text-slate-200 transition-colors">YouTube</a>
        </div>
      </div>

      <div class="pt-4 border-t border-slate-800/40 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-500">
        <div>
          &copy; <span id="current-year">2026</span> Dragoș Iorgulescu &middot; Bucharest, RO
        </div>
        <div class="flex items-center gap-2">
          <span>Zero trackers &middot; Pure HTML &amp; CSS &middot; Host: Namebox.ro</span>
        </div>
      </div>
    </div>
  </footer>

  <script src="{root_path}js/tactical.js"></script>
</body>
</html>
"""

# --- Article Page Generator ---
def generate_single_article(meta, content_html, category, slug):
    target_dir = OUTPUT_DIR / category / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    title = meta.get("title", slug.capitalize())
    date_iso = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
    date_display = format_display_date(date_iso)
    read_time = meta.get("read_time", "5 MIN READ")

    content_clean = clean_content_paths(content_html, depth=2)

    cat_labels = {
        "blog": "Journal",
        "howto": "How-To",
        "programe": "Programs"
    }
    cat_label = cat_labels.get(category, category.capitalize())

    page_html = f"""{get_html_head(f"{title} // {cat_label}", depth=2)}
{get_header(active_nav=category, depth=2)}

<main class="max-w-3xl mx-auto px-4 sm:px-6 py-10 sm:py-14">
  <div class="mb-8">
    <a href="../../{category}/" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors">
      ← {cat_label}
    </a>
  </div>

  <header class="mb-10 pb-6 border-b border-slate-800">
    <div class="flex items-center gap-2 font-mono text-xs text-slate-400 mb-3">
      <time datetime="{date_iso}">{date_display}</time>
      <span class="text-slate-600">&middot;</span>
      <span>{read_time}</span>
    </div>

    <h1 class="font-display font-bold text-2xl sm:text-4xl text-slate-100 leading-tight">
      {title}
    </h1>
  </header>

  <article class="prose-tactical text-slate-300">
    {content_clean}
  </article>

  <div class="mt-12 pt-6 border-t border-slate-800 flex items-center justify-between font-mono text-xs text-slate-400">
    <a href="../../{category}/" class="hover:text-amber-400 transition-colors">
      ← Back to {cat_label}
    </a>
    <a href="#" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;" class="hover:text-amber-400 transition-colors">
      Back to top ↑
    </a>
  </div>
</main>

{get_footer(depth=2)}"""

    with open(target_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(page_html)

# --- Category Index Generator ---
def generate_category_index(category, items):
    output_dir = OUTPUT_DIR / category
    output_dir.mkdir(parents=True, exist_ok=True)

    category_titles = {
        "blog": "Journal",
        "howto": "Technical Guides & How-Tos",
        "programe": "Training Frameworks"
    }
    category_descriptions = {
        "blog": "Essays and reflections on software testing, physical strength, minimal computing, and life balance.",
        "howto": "Step-by-step technical guides, Unix configurations, homelab setups, and systems engineering protocols.",
        "programe": "Structured physical preparation frameworks, kettlebell progressions, and conditioning protocols."
    }

    entries_html = ""
    for item in items:
        date_display = item.get("date_display", item.get("date", ""))
        read_time = item.get("read_time", "5 MIN READ")
        title = item.get("title", item["slug"].capitalize())
        excerpt = item.get("excerpt", "")

        entries_html += f"""
      <article class="py-5 border-b border-slate-800 group journal-entry">
        <div class="flex items-center gap-2 font-mono text-xs text-slate-500 mb-1.5">
          <time datetime="{item['date']}">{date_display}</time>
          <span class="text-slate-700">&middot;</span>
          <span>{read_time}</span>
        </div>
        <h2 class="font-display font-bold text-lg text-slate-100 group-hover:text-amber-400 transition-colors mb-2">
          <a href="{item['slug']}/">{title}</a>
        </h2>
        <p class="text-sm text-slate-400 font-sans leading-relaxed">
          {excerpt}
        </p>
      </article>"""

    cat_title = category_titles.get(category, category.capitalize())
    cat_desc = category_descriptions.get(category, "")

    page_html = f"""{get_html_head(f"{cat_title} // Directory", depth=1)}
{get_header(active_nav=category, depth=1)}

<main class="max-w-4xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
  <div class="mb-6">
    <a href="../" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors">
      ← Home
    </a>
  </div>

  <header class="mb-10 pb-6 border-b border-slate-800">
    <h1 class="font-display font-bold text-3xl sm:text-4xl text-slate-100 mb-3">
      {cat_title}
    </h1>
    <p class="text-sm font-sans text-slate-400 max-w-2xl leading-relaxed mb-6">
      {cat_desc}
    </p>

    <!-- Search / Filter input -->
    <div class="max-w-md">
      <input 
        id="hud-filter-input"
        data-target=".journal-entry"
        type="text" 
        placeholder="Filter by keyword..." 
        class="w-full px-3 py-2 rounded-lg bg-[#0B0F17] border border-slate-800 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/60 transition-colors"
      >
    </div>
  </header>

  <div class="space-y-1">
    {entries_html}
  </div>
</main>

{get_footer(depth=1)}"""

    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(page_html)

def copy_static_assets():
    """
    Copies static assets (css, js, images) and standalone sections (programe, sounds, kettlebell)
    from workspace sources into the public/ output directory.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    asset_folders = ["css", "js", "images", "programe", "sounds", "kettlebell"]
    for folder in asset_folders:
        src = BASE_DIR / folder
        dst = OUTPUT_DIR / folder
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)

    # Any standalone root files like favicon
    for filename in ["favicon.ico", "CNAME"]:
        extra_src = BASE_DIR / filename
        if extra_src.is_file():
            shutil.copy2(extra_src, OUTPUT_DIR / filename)

# --- Home Page Generator ---
def generate_home_page(posts, guides):
    # Top 5 latest blog posts
    posts_list_html = ""
    for item in posts[:5]:
        date_display = item.get("date_display", item.get("date", ""))
        read_time = item.get("read_time", "5 MIN READ")
        title = item.get("title", item["slug"].capitalize())
        posts_list_html += f"""
      <article class="group py-2.5 flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 sm:gap-4 border-b border-slate-800/40 hover:border-slate-700/60 transition-colors">
        <div class="flex-1">
          <a href="blog/{item['slug']}/" class="font-display font-medium text-slate-200 group-hover:text-amber-400 transition-colors text-sm sm:text-base">
            {title}
          </a>
        </div>
        <div class="flex items-center gap-2 font-mono text-xs text-slate-500 flex-shrink-0">
          <span>{read_time}</span>
          <span class="text-slate-700">&middot;</span>
          <time datetime="{item['date']}">{date_display}</time>
        </div>
      </article>"""

    # Top 5 latest guides
    guides_list_html = ""
    for item in guides[:5]:
        date_display = item.get("date_display", item.get("date", ""))
        read_time = item.get("read_time", "5 MIN READ")
        title = item.get("title", item["slug"].capitalize())
        guides_list_html += f"""
      <article class="group py-2.5 flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 sm:gap-4 border-b border-slate-800/40 hover:border-slate-700/60 transition-colors">
        <div class="flex-1">
          <a href="howto/{item['slug']}/" class="font-display font-medium text-slate-200 group-hover:text-amber-400 transition-colors text-sm sm:text-base">
            {title}
          </a>
        </div>
        <div class="flex items-center gap-2 font-mono text-xs text-slate-500 flex-shrink-0">
          <span>{read_time}</span>
          <span class="text-slate-700">&middot;</span>
          <time datetime="{item['date']}">{date_display}</time>
        </div>
      </article>"""

    home_html = f"""{get_html_head("Dragoș Iorgulescu", depth=0)}
{get_header(depth=0)}

<main class="max-w-4xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
  <!-- HERO SECTION -->
  <section class="mb-14">
    <h1 class="font-display font-bold text-3xl sm:text-5xl text-slate-100 tracking-tight leading-tight mb-3">
      Dragoș Iorgulescu
    </h1>
    <p class="font-mono text-xs uppercase tracking-wider text-amber-400 mb-5">
      Test Engineer &middot; Strength Practitioner &middot; Bucharest, RO
    </p>
    <p class="text-base sm:text-lg text-slate-300 font-sans leading-relaxed max-w-2xl mb-3">
      Husband, father of two boys. Software Test Engineer, kettlebell lifter, and audio explorer. Dedicated to minimal tools, robust physical conditioning, and honest engineering across open and proprietary platforms.
    </p>
    <p class="text-sm text-slate-400 font-sans leading-relaxed max-w-2xl mb-6">
      See what I'm currently focused on right now on my <a href="now.html" class="text-amber-400 hover:underline font-medium">now page</a>.
    </p>
    <div class="flex flex-wrap gap-4 text-xs font-mono text-slate-400">
      <a href="blog/" class="hover:text-amber-400 transition-colors">→ Journal ({len(posts):02d})</a>
      <a href="programe/" class="hover:text-amber-400 transition-colors">→ Programs (03)</a>
      <a href="howto/" class="hover:text-amber-400 transition-colors">→ How-To ({len(guides):02d})</a>
      <a href="sounds/" class="hover:text-amber-400 transition-colors">→ Sounds (05)</a>
    </div>
  </section>

  <!-- JOURNAL SECTION -->
  <section class="mb-14">
    <div class="flex items-center justify-between pb-2 mb-4 border-b border-slate-800">
      <h2 class="font-display font-bold text-xl text-slate-100 tracking-tight">
        Recent Journal Entries
      </h2>
      <a href="blog/" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors">
        All entries ({len(posts)}) →
      </a>
    </div>

    <div class="space-y-1">
      {posts_list_html}
    </div>
  </section>

  <!-- TRAINING FRAMEWORKS -->
  <section class="mb-14">
    <div class="flex items-center justify-between pb-2 mb-4 border-b border-slate-800">
      <h2 class="font-display font-bold text-xl text-slate-100 tracking-tight">
        Training Frameworks
      </h2>
      <a href="programe/" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors">
        All Programs →
      </a>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <a href="programe/tension-spectrum/" class="tactical-card p-5 flex flex-col justify-between transition-all group">
        <div>
          <div class="font-mono text-[11px] text-slate-500 uppercase tracking-wider mb-2">01 // Hypertrophy &amp; Tension</div>
          <h3 class="font-display font-bold text-base text-slate-100 group-hover:text-amber-400 transition-colors mb-2">Tension Spectrum</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Functional hypertrophy without CNS exhaustion. 5-day hybrid split.</p>
        </div>
      </a>

      <a href="programe/sfg-prep/" class="tactical-card p-5 flex flex-col justify-between transition-all group">
        <div>
          <div class="font-mono text-[11px] text-slate-500 uppercase tracking-wider mb-2">02 // 8-Month Certification</div>
          <h3 class="font-display font-bold text-base text-slate-100 group-hover:text-amber-400 transition-colors mb-2">SFG I &amp; SFB Prep</h3>
          <p class="text-xs text-slate-400 leading-relaxed">8-month progressive plan for StrongFirst Girya 1 &amp; Bodyweight certifications.</p>
        </div>
      </a>

      <a href="programe/bjj-prep/" class="tactical-card p-5 flex flex-col justify-between transition-all group">
        <div>
          <div class="font-mono text-[11px] text-slate-500 uppercase tracking-wider mb-2">03 // Rehab &amp; Aerobic Base</div>
          <h3 class="font-display font-bold text-base text-slate-100 group-hover:text-amber-400 transition-colors mb-2">BJJ Prep &amp; Rehabilitation</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Elbow tendonitis rehabilitation, daily micro-routine &amp; Zone 2 aerobic base.</p>
        </div>
      </a>
    </div>
  </section>

  <!-- HOW-TO GUIDES -->
  <section class="mb-14">
    <div class="flex items-center justify-between pb-2 mb-4 border-b border-slate-800">
      <h2 class="font-display font-bold text-xl text-slate-100 tracking-tight">
        Technical Guides &amp; How-Tos
      </h2>
      <a href="howto/" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors">
        All guides ({len(guides)}) →
      </a>
    </div>

    <div class="space-y-1">
      {guides_list_html}
    </div>
  </section>

  <!-- PROJECTS & AUDIO -->
  <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <div class="tactical-card p-5">
      <div class="flex items-center justify-between pb-2 mb-3 border-b border-slate-800">
        <h3 class="font-display font-bold text-base text-slate-100">Open Source &amp; Tools</h3>
        <a href="https://github.com/diorgulescu" target="_blank" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors">github.com/diorgulescu ↗</a>
      </div>
      <ul class="space-y-3 font-sans text-xs text-slate-300">
        <li>
          <div class="flex items-center gap-2">
            <a href="https://github.com/diorgulescu/tcpflowy" target="_blank" class="font-mono font-semibold text-slate-100 hover:text-amber-400 hover:underline">tcpflowy →</a>
            <span class="tag">v1.0.0 &bull; PyPI</span>
          </div>
          <span class="text-slate-400 block mt-0.5">Terminal network flow analysis &amp; TCP visualization tool, available on <a href="https://pypi.org/project/tcpflowy/" target="_blank" class="text-amber-400 hover:underline">PyPI</a>.</span>
        </li>
        <li>
          <div class="flex items-center gap-2">
            <a href="https://github.com/diorgulescu/GirevoyPulse" target="_blank" class="font-mono font-semibold text-slate-100 hover:text-amber-400 hover:underline">GirevoyPulse →</a>
            <span class="tag">Xcode &amp; Android Studio</span>
          </div>
          <span class="text-slate-400 block mt-0.5">Real-time heart-rate telemetry &amp; pace monitor for kettlebell sport and alactic conditioning.</span>
        </li>
        <li>
          <div class="flex items-center gap-2">
            <a href="https://github.com/diorgulescu/DAMF" target="_blank" class="font-mono font-semibold text-slate-100 hover:text-amber-400 hover:underline">DAMF →</a>
            <span class="tag">Updated</span>
          </div>
          <span class="text-slate-400 block mt-0.5">Device automation framework for embedded hardware testing and lab validation.</span>
        </li>
        <li>
          <div class="flex items-center gap-2">
            <a href="https://github.com/diorgulescu/suckless-debian" target="_blank" class="font-mono font-semibold text-slate-100 hover:text-amber-400 hover:underline">suckless-debian →</a>
            <span class="tag">amd64 &bull; ARM &bull; i386</span>
          </div>
          <span class="text-slate-400 block mt-0.5">Minimalist keyboard-driven Debian environment built on dwm, dmenu, and st with multi-arch support.</span>
        </li>
      </ul>
    </div>

    <div class="tactical-card p-5 flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between pb-2 mb-3 border-b border-slate-800">
          <h3 class="font-display font-bold text-base text-slate-100">Audio Labs &amp; Modular</h3>
          <a href="sounds/" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors">sounds/ ↗</a>
        </div>
        <div class="space-y-3 font-sans text-xs text-slate-300 mb-4">
          <div>
            <div class="flex items-center gap-2">
              <a href="https://github.com/voidwave-lab" target="_blank" class="font-mono font-semibold text-slate-100 hover:text-amber-400 hover:underline">voidwave-lab →</a>
              <span class="tag">4 Open Source Tools</span>
            </div>
            <span class="text-slate-400 block mt-0.5">DSP audio generators for experimental, glitch &amp; ambient music: Modular Synth, MS-20 mini clone, test equipment studio, and Aetherium generative ambient sanctuary.</span>
          </div>
          <div>
            <span class="font-mono font-semibold text-slate-200">Musical Archives &amp; Releases</span>
            <span class="text-slate-400 block mt-0.5">Over 15 years exploring hardware modular synthesis, drone soundscapes, field recordings, and raw living-room sessions.</span>
          </div>
        </div>
      </div>
      <div class="pt-3 border-t border-slate-800">
        <a href="sounds/" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors flex items-center justify-between">
          <span>Explore sound archives &amp; DSP tools (5 monikers)</span>
          <span>→</span>
        </a>
      </div>
    </div>
  </section>
</main>

{get_footer(depth=0)}"""

    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(home_html)

def generate_now_page():
    """
    Compiles now.html from content/now.md if it exists.
    """
    now_md = BASE_DIR / "content" / "now.md"
    if not now_md.exists():
        return False

    with open(now_md, "r", encoding="utf-8") as fp:
        raw = fp.read()

    meta, content_html, body = parse_markdown(raw)
    title = meta.get("title", "What I'm Doing Now")
    updated = meta.get("updated", meta.get("date", "October 2026"))
    location = meta.get("location", "Bucharest, RO")
    tag = meta.get("tag", "PRIORITIES & WORK IN PROGRESS")

    content_clean = clean_content_paths(content_html, depth=0)

    now_html = f"""{get_html_head(f"{title}", depth=0)}
{get_header(active_nav="now", depth=0)}

<main class="max-w-3xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
  <div class="mb-8">
    <a href="./" class="font-mono text-xs text-slate-400 hover:text-amber-400 transition-colors">
      ← Home
    </a>
  </div>

  <!-- PAGE HEADER -->
  <header class="mb-10 pb-6 border-b border-slate-800/60">
    <div class="font-mono text-xs text-slate-400 mb-2">
      {location} &middot; Updated {updated}
    </div>
    <h1 class="font-display font-bold text-3xl sm:text-4xl text-slate-100 tracking-tight mb-2">
      {title}
    </h1>
    <p class="font-mono text-xs text-slate-400 uppercase tracking-wider">
      {tag}
    </p>
  </header>

  <!-- CONTENT -->
  <article class="prose-tactical text-slate-300">
    {content_clean}
  </article>
</main>

{get_footer(depth=0)}"""

    with open(OUTPUT_DIR / "now.html", "w", encoding="utf-8") as fp:
        fp.write(now_html)
    print("[SYS // NOW] Generated public/now.html from content/now.md")
    return True

def generate_sitemap(blog_items, howto_items):
    """
    Generates sitemap.xml and robots.txt in the website root directory.
    Includes all core sections, training programs, blog articles, and how-to guides.
    """
    base_url = SITE_CONFIG.get("site_url", "https://iorgos.net").rstrip("/")
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Determine latest dates for sections
    latest_blog_date = blog_items[0]["date"] if blog_items else today_str
    latest_howto_date = howto_items[0]["date"] if howto_items else today_str

    # Date for now page
    now_date = today_str
    now_md = BASE_DIR / "content" / "now.md"
    if now_md.exists():
        try:
            m_time = datetime.fromtimestamp(now_md.stat().st_mtime).strftime("%Y-%m-%d")
            now_date = m_time
        except Exception:
            pass

    # Date for kettlebell guide
    kettlebell_date = today_str
    kb_md = BASE_DIR / "content" / "kettlebell.md"
    if kb_md.exists():
        try:
            k_time = datetime.fromtimestamp(kb_md.stat().st_mtime).strftime("%Y-%m-%d")
            kettlebell_date = k_time
        except Exception:
            pass

    # Core URL list: (url_path, lastmod, changefreq, priority)
    urls = [
        ("/", today_str, "weekly", "1.0"),
        ("/now.html", now_date, "weekly", "0.9"),
        ("/programe/", today_str, "weekly", "0.9"),
        ("/programe/tension-spectrum/", today_str, "monthly", "0.8"),
        ("/programe/sfg-prep/", today_str, "monthly", "0.8"),
        ("/programe/bjj-prep/", today_str, "monthly", "0.8"),
        ("/kettlebell/", kettlebell_date, "monthly", "0.8"),
        ("/sounds/", today_str, "monthly", "0.8"),
        ("/blog/", str(latest_blog_date)[:10], "weekly", "0.8"),
        ("/howto/", str(latest_howto_date)[:10], "weekly", "0.8"),
    ]

    # Add all blog articles
    for item in blog_items:
        date_val = str(item.get("date", today_str)).strip().strip('"').strip("'")[:10]
        urls.append((f"/blog/{item['slug']}/", date_val, "monthly", "0.7"))

    # Add all howto guides
    for item in howto_items:
        date_val = str(item.get("date", today_str)).strip().strip('"').strip("'")[:10]
        urls.append((f"/howto/{item['slug']}/", date_val, "monthly", "0.7"))

    # Build XML
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for path, lastmod, freq, prio in urls:
        full_loc = f"{base_url}{path}" if path.startswith("/") else f"{base_url}/{path}"
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{full_loc}</loc>")
        xml_lines.append(f"    <lastmod>{lastmod}</lastmod>")
        xml_lines.append(f"    <changefreq>{freq}</changefreq>")
        xml_lines.append(f"    <priority>{prio}</priority>")
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>\n")
    sitemap_content = "\n".join(xml_lines)

    sitemap_file = OUTPUT_DIR / "sitemap.xml"
    with open(sitemap_file, "w", encoding="utf-8") as fp:
        fp.write(sitemap_content)
    print(f"[SYS // SITEMAP] Generated public/sitemap.xml with {len(urls)} URLs")

    # Generate robots.txt
    robots_content = f"""# robots.txt for {base_url}
User-agent: *
Allow: /

# Sitemap location
Sitemap: {base_url}/sitemap.xml
"""
    robots_file = OUTPUT_DIR / "robots.txt"
    with open(robots_file, "w", encoding="utf-8") as fp:
        fp.write(robots_content)
    print("[SYS // ROBOTS] Generated public/robots.txt")


def generate_rss_feed(blog_items):
    """
    Generates RSS 2.0 feed for the blog section at public/feed.xml
    and public/blog/feed.xml for better compatibility.
    """
    if not blog_items:
        print("[WARN // RSS] No blog items found, skipping RSS feed generation")
        return

    base_url = SITE_CONFIG.get("site_url", "https://iorgos.net").rstrip("/")
    site_title = SITE_CONFIG.get("author", "Dragoș Iorgulescu")
    site_description = "Personal website, training frameworks, technical how-tos, and audio archives by Dragoș Iorgulescu."
    from datetime import timezone
    now = datetime.now(timezone.utc)
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Sort blog items by date descending (newest first)
    sorted_items = sorted(blog_items, key=lambda x: str(x["date"]), reverse=True)

    rss_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        f'  <channel>',
        f'    <title>{html.escape(site_title)}</title>',
        f'    <link>{base_url}</link>',
        f'    <description>{html.escape(site_description)}</description>',
        f'    <language>ro-RO</language>',
        f'    <pubDate>{pub_date}</pubDate>',
        f'    <lastBuildDate>{pub_date}</lastBuildDate>',
        f'    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml"/>',
        f'    <generator>Tactical Dark Static Site Generator</generator>',
        f'    <docs>http://www.rssboard.org/rss-specification/</docs>',
    ]

    author_name = SITE_CONFIG.get("author", "Dragoș Iorgulescu")
    author_email = SITE_CONFIG.get("email", "dragos@iorgos.net")
    
    for item in sorted_items:
        slug = item["slug"]
        title = item.get("title", slug.capitalize())
        link = f"{base_url}/blog/{slug}/"
        pub_date_item = item.get("date", "2021-01-01")
        
        try:
            dt = datetime.strptime(str(pub_date_item).strip().split()[0], "%Y-%m-%d")
            rfc_date = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        except (ValueError, TypeError):
            rfc_date = pub_date
        
        description = item.get("excerpt", "")
        if not description:
            description = f"Journal dispatch: {title}"
        
        # Clean description for RSS - ensure it's valid CDATA
        description_clean = description.strip()
        
        tag = item.get("tag", "Journal")
        
        rss_lines.append(f'    <item>')
        rss_lines.append(f'      <title>{html.escape(title)}</title>')
        rss_lines.append(f'      <link>{link}</link>')
        rss_lines.append(f'      <guid isPermaLink="true">{link}</guid>')
        rss_lines.append(f'      <pubDate>{rfc_date}</pubDate>')
        rss_lines.append(f'      <author>{html.escape(author_email)} ({html.escape(author_name)})</author>')
        rss_lines.append(f'      <category>{html.escape(tag)}</category>')
        rss_lines.append(f'      <description><![CDATA[{description_clean}]]></description>')
        rss_lines.append(f'    </item>')

    rss_lines.append(f'  </channel>')
    rss_lines.append(f'</rss>')
    rss_content = "\n".join(rss_lines) + "\n"

    # Write main feed at root
    feed_file = OUTPUT_DIR / "feed.xml"
    with open(feed_file, "w", encoding="utf-8") as fp:
        fp.write(rss_content)
    print(f"[SYS // RSS] Generated public/feed.xml with {len(sorted_items)} blog entries")

    # Also write to blog/feed.xml for compatibility
    blog_feed_file = OUTPUT_DIR / "blog" / "feed.xml"
    with open(blog_feed_file, "w", encoding="utf-8") as fp:
        fp.write(rss_content)
    print(f"[SYS // RSS] Generated public/blog/feed.xml")


# --- Core Scanner & Rebuilder ---
def load_and_compile_all():
    content_dir = BASE_DIR / "content"
    if not content_dir.exists():
        print(f"[ERR // CONTENT] content/ directory not found at {content_dir}")
        return [], []

    # 1. Copy static assets and sections into public/
    copy_static_assets()

    blog_items = []
    howto_items = []

    # 2. Process Blog
    blog_dir = content_dir / "blog"
    if blog_dir.exists():
        for md_file in sorted(blog_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            with open(md_file, "r", encoding="utf-8") as fp:
                raw = fp.read()
            meta, content_html, body = parse_markdown(raw)

            slug = meta.get("slug") or md_file.stem

            # Check draft status
            is_draft = str(meta.get("draft", "false")).lower() in ["true", "1", "yes"]
            if is_draft:
                draft_dir = OUTPUT_DIR / "blog" / slug
                if draft_dir.is_dir():
                    shutil.rmtree(draft_dir)
                    print(f"[SYS // DRAFT] Removed unlisted HTML directory for draft: public/blog/{slug}/")
                continue

            title = meta.get("title") or slug.replace("-", " ").capitalize()
            date_iso = meta.get("date", "2021-01-01")
            date_display = format_display_date(date_iso)

            # Auto excerpt
            excerpt = meta.get("excerpt")
            if not excerpt:
                paras = [p.strip() for p in body.split('\n\n') if p.strip() and not p.startswith('#') and not p.startswith('![')]
                excerpt = (paras[0][:180] + '...') if paras else "Journal dispatch."

            # Auto read time
            words = len(body.split())
            read_time = meta.get("read_time", f"{max(1, math.ceil(words / 200))} MIN READ")

            item = {
                "slug": slug,
                "title": title,
                "date": date_iso,
                "date_display": date_display,
                "excerpt": excerpt,
                "read_time": read_time,
                "tag": meta.get("tag", "JOURNAL // ESSAY"),
                "badge_class": meta.get("badge_class", meta.get("badge", "badge-emerald")),
                "content_html": content_html
            }

            generate_single_article(item, content_html, "blog", slug)
            blog_items.append(item)

    # Automatic cleanup of orphaned blog directories in public/
    active_blog_slugs = {item["slug"] for item in blog_items}
    blog_root = OUTPUT_DIR / "blog"
    if blog_root.exists():
        for sub in blog_root.iterdir():
            if sub.is_dir() and sub.name not in active_blog_slugs and not sub.name.startswith(("_", ".")):
                shutil.rmtree(sub)
                print(f"[SYS // CLEANUP] Removed orphaned article directory: public/blog/{sub.name}/")

    blog_items.sort(key=lambda x: str(x["date"]), reverse=True)
    generate_category_index("blog", blog_items)

    # 3. Process Howto
    howto_dir = content_dir / "howto"
    if howto_dir.exists():
        for md_file in sorted(howto_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            with open(md_file, "r", encoding="utf-8") as fp:
                raw = fp.read()
            meta, content_html, body = parse_markdown(raw)

            slug = meta.get("slug") or md_file.stem

            is_draft = str(meta.get("draft", "false")).lower() in ["true", "1", "yes"]
            if is_draft:
                draft_dir = OUTPUT_DIR / "howto" / slug
                if draft_dir.is_dir():
                    shutil.rmtree(draft_dir)
                    print(f"[SYS // DRAFT] Removed unlisted HTML directory for draft: public/howto/{slug}/")
                continue

            title = meta.get("title") or slug.replace("-", " ").capitalize()
            date_iso = meta.get("date", "2020-01-01")
            date_display = format_display_date(date_iso)

            excerpt = meta.get("excerpt")
            if not excerpt:
                paras = [p.strip() for p in body.split('\n\n') if p.strip() and not p.startswith('#') and not p.startswith('![')]
                excerpt = (paras[0][:180] + '...') if paras else "Technical documentation."

            words = len(body.split())
            read_time = meta.get("read_time", f"{max(1, math.ceil(words / 200))} MIN READ")

            item = {
                "slug": slug,
                "title": title,
                "date": date_iso,
                "date_display": date_display,
                "excerpt": excerpt,
                "read_time": read_time,
                "tag": meta.get("tag", "SYSADMIN // TECH"),
                "badge_class": meta.get("badge_class", meta.get("badge", "badge-sky")),
                "content_html": content_html
            }

            generate_single_article(item, content_html, "howto", slug)
            howto_items.append(item)

    # Automatic cleanup of orphaned howto directories in public/
    active_howto_slugs = {item["slug"] for item in howto_items}
    howto_root = OUTPUT_DIR / "howto"
    if howto_root.exists():
        for sub in howto_root.iterdir():
            if sub.is_dir() and sub.name not in active_howto_slugs and not sub.name.startswith(("_", ".")):
                shutil.rmtree(sub)
                print(f"[SYS // CLEANUP] Removed orphaned guide directory: public/howto/{sub.name}/")

    howto_items.sort(key=lambda x: str(x["date"]), reverse=True)
    generate_category_index("howto", howto_items)

    # 4. Rebuild Home Page
    generate_home_page(blog_items, howto_items)

    # 5. Rebuild Now Page
    generate_now_page()

    # 6. Synchronize static pages (programe/, sounds/, kettlebell/)
    sync_static_headers()

    # 7. Generate Sitemap & Robots.txt
    generate_sitemap(blog_items, howto_items)

    # 8. Generate RSS Feed for Blog
    generate_rss_feed(blog_items)

    return blog_items, howto_items

def sync_static_headers():
    """
    Synchronizes minimalist header and footer across all standalone static pages
    (sounds/, programe/, kettlebell/) in both public/ and source directories.
    """
    theme_script = """  <!-- Zero-FOUC Theme Initializer -->
  <script>
    (function() {
      var stored = localStorage.getItem('theme_preference');
      var theme = stored || (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
      document.documentElement.classList.remove('dark', 'light');
      document.documentElement.classList.add(theme);
      document.documentElement.setAttribute('data-theme', theme);
    })();
  </script>"""

    for root_dir in [OUTPUT_DIR, BASE_DIR]:
        if not root_dir.exists():
            continue
        for html_file in root_dir.glob("**/*.html"):
            if "_legacy_hugo" in html_file.parts or "_backup_tactical_hud" in html_file.parts or "content" in html_file.parts:
                continue
            if root_dir == BASE_DIR and "public" in html_file.parts:
                continue
            rel_parts = html_file.relative_to(root_dir).parts
            if not rel_parts:
                continue
            depth = len(rel_parts) - 1
            first_part = rel_parts[0].lower()

            if first_part in ["programe", "sounds", "kettlebell"]:
                active_nav = first_part
                try:
                    content = html_file.read_text(encoding="utf-8")
                    orig = content

                    # 1. Update <html lang="ro" class="dark"> to <html lang="ro">
                    content = re.sub(r'<html\s+lang="ro"\s+class="dark">', '<html lang="ro">', content)

                    # 1b. Strip external CDNs for autonomous / frugal offline loading
                    content = re.sub(r'<!-- Google Fonts:[\s\S]*?rel="stylesheet">\s*', '', content)
                    content = re.sub(r'<link rel="preconnect"[\s\S]*?rel="stylesheet">\s*', '', content)
                    content = re.sub(r'<!-- Phosphor Icons -->\s*<script src="https://unpkg.com/@phosphor-icons/web"></script>\s*', '', content)
                    content = re.sub(r'<script src="https://unpkg.com/@phosphor-icons/web"></script>\s*', '', content)
                    content = re.sub(r'<!-- Tailwind CSS CDN -->\s*', '', content)
                    content = re.sub(r'<script src="https://cdn.tailwindcss.com"></script>\s*', '', content)
                    content = re.sub(r'<script>\s*tailwind\.config\s*=\s*\{[\s\S]*?\}\s*</script>\s*', '', content)

                    # 2. Add zero-fouc script if missing
                    if "theme_preference" not in content and "</head>" in content:
                        content = content.replace("</head>", f"{theme_script}\n</head>")

                    # 3. Add sitemap link if missing
                    root_path = "./" if depth == 0 else "../" * depth
                    sitemap_link = f'  <link rel="sitemap" type="application/xml" title="Sitemap" href="{root_path}sitemap.xml">'
                    if 'rel="sitemap"' not in content and "</head>" in content:
                        content = content.replace("</head>", f"{sitemap_link}\n</head>")

                    # Strip old top HUD bar and duplicate minimal comments
                    content = re.sub(r'<!-- MINIMAL NAVBAR -->\s*', '', content)
                    content = re.sub(r'<!-- TOP (?:HUD|TELEMETRY HUD) BAR -->[\s\S]*?</div>\s*</div>\s*(?=\s*<!-- [A-Z\s]+NAVBAR -->|<header)', '', content)
                    content = re.sub(r'<!-- (?:TOP|MAIN) TACTICAL NAVBAR -->\s*', '', content)
                    content = re.sub(r'<!-- CLEAN EDITORIAL NAVBAR -->\s*', '', content)

                    # Replace ONLY the first header (the top navbar)
                    minimal_hdr = get_header(active_nav=active_nav, depth=depth).strip()
                    content = re.sub(r'<header[\s\S]*?</header>', minimal_hdr, content, count=1)
                    
                    minimal_ftr = get_footer(depth=depth).strip()
                    content = re.sub(r'(?:<!-- (?:TACTICAL FOOTER HUD|MINIMAL FOOTER) -->\s*)*<footer[\s\S]*?</html>', minimal_ftr, content)

                    if content != orig:
                        html_file.write_text(content, encoding="utf-8")
                except Exception as e:
                    print(f"[WARN] Error syncing {html_file}: {e}")

# --- Single File Ingest / Publishing ---
def publish_markdown_file(filepath, forced_category=None):
    p = Path(filepath)
    if not p.is_file():
        print(f"[ERR // FILE] File does not exist: {filepath}")
        sys.exit(1)

    # Special handling for now.md
    if p.name == "now.md":
        target = BASE_DIR / "content" / "now.md"
        if p.resolve() != target.resolve():
            shutil.copy2(p, target)
        generate_now_page()
        print(f"[SYS // PUBLISH] Successfully updated now.html from {p.name}")
        return

    with open(p, "r", encoding="utf-8") as f:
        raw_content = f.read()

    meta, content_html, body = parse_markdown(raw_content)

    # Determine category
    category = forced_category or meta.get("category")
    if not category:
        # Check parent folder name
        parent_name = p.parent.name.lower()
        if parent_name in ["blog", "howto", "programe"]:
            category = parent_name
        else:
            category = "blog" # default

    category = category.lower().strip()
    if category not in ["blog", "howto", "programe"]:
        print(f"[WARN // CATEGORY] Unrecognized category '{category}', defaulting to 'blog'")
        category = "blog"

    # Title & slug
    title = meta.get("title")
    if not title:
        # Look for first heading
        first_h = re.search(r'^#\s+(.*?)$', body, re.MULTILINE)
        if first_h:
            title = first_h.group(1).strip()
        else:
            title = p.stem.replace("-", " ").capitalize()
        meta["title"] = title

    slug = meta.get("slug")
    if not slug:
        slug = slugify(p.stem) if p.stem != "draft" else slugify(title)
        meta["slug"] = slug

    # Date
    if "date" not in meta:
        meta["date"] = datetime.now().strftime("%Y-%m-%d")

    # Destination in content/
    dest_content_dir = BASE_DIR / "content" / category
    dest_content_dir.mkdir(parents=True, exist_ok=True)
    dest_md_path = dest_content_dir / f"{slug}.md"

    # Copy / update content source
    shutil.copy2(p, dest_md_path)
    print(f"[SYS // INGEST] Source file saved to: {dest_md_path.relative_to(BASE_DIR)}")

    # Check draft
    is_draft = str(meta.get("draft", "false")).lower() in ["true", "1", "yes"]
    if is_draft:
        print(f"[SYS // DRAFT] Article marked as draft. Saved to content/, skipping HTML compilation.")
        return

    # Trigger site rebuild to integrate the new post into indexes, home, counts
    print(f"[SYS // COMPILE] Compiling public/{category}/{slug}/index.html...")
    blog_items, howto_items = load_and_compile_all()

    print("\n" + "=" * 65)
    print(f" [TACTICAL HUD // PUBLISHED SUCCESSFULLY]")
    print(f"  Category:      {category.upper()}")
    print(f"  Title:         {title}")
    print(f"  Slug:          {slug}")
    print(f"  Date:          {meta['date']} ({format_display_date(meta['date'])})")
    print(f"  HTML URL:      public/{category}/{slug}/index.html")
    print(f"  Total Blog:    {len(blog_items)} articles")
    print(f"  Total How-To:  {len(howto_items)} guides")
    print("=" * 65)

# --- Scaffold Draft Template ---
def scaffold_draft(title, category="blog", tag=None):
    slug = slugify(title)
    dest_dir = BASE_DIR / "content" / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    target_file = dest_dir / f"{slug}.md"

    if target_file.exists():
        print(f"[WARN // EXISTS] File already exists: {target_file}")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    default_tag = tag or ("TECH // GUIDE" if category == "howto" else "JOURNAL // ESSAY")
    badge_cls = "badge-sky" if category == "howto" else "badge-emerald"

    template = f"""---
title: "{title}"
date: {today}
category: {category}
slug: {slug}
tag: "{default_tag}"
badge_class: {badge_cls}
excerpt: "Scurt rezumat al acestui articol pentru cardul din grila Bento."
read_time: "5 MIN READ"
draft: false
---

Aici începe primul paragraf al noului tău articol. Textul este redactat în format Markdown standard.

## Prima Secțiune Tehnică

Poți folosi liste, cod și blocuri formatate:

- Punctul unu din analiză
- Punctul doi cu accent pe **performanță** și *simplitate*
- Referință către alte comenzi sau instrumente

```bash
# Exemplu de comandă executabilă
echo "Sistem static Tactical Dark HUD operațional"
```

> „Simplitatea este condiția preliminară pentru fiabilitate.” — Edsger W. Dijkstra
"""
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"[SYS // NEW] Draft template created at: {target_file.relative_to(BASE_DIR)}")
    print(f"To compile after editing: python3 publish.py {target_file.relative_to(BASE_DIR)}")

# --- Article Deletion / Cleanup ---
def delete_article(slug_or_path, forced_category=None):
    """
    Deletes an article from content/ and its generated HTML folder, then rebuilds the site.
    """
    p = Path(slug_or_path)
    slug = p.stem
    if slug == "index" and p.parent.name:
        slug = p.parent.name

    categories = [forced_category] if forced_category else ["blog", "howto", "programe"]
    deleted_md = False
    deleted_html = False

    for cat in categories:
        md_file = BASE_DIR / "content" / cat / f"{slug}.md"
        if md_file.is_file():
            md_file.unlink()
            print(f"[SYS // DELETE] Removed source markdown: content/{cat}/{slug}.md")
            deleted_md = True

        for target_root in [OUTPUT_DIR, BASE_DIR]:
            html_dir = target_root / cat / slug
            if html_dir.is_dir():
                shutil.rmtree(html_dir)
                print(f"[SYS // CLEANUP] Removed HTML directory: {target_root.name}/{cat}/{slug}/")
                deleted_html = True

    if not deleted_md and not deleted_html:
        print(f"[WARN // NOT FOUND] No article or directory found matching '{slug_or_path}'.")
        return False

    print(f"\n[SYS // REBUILD] Rebuilding site indexes and HUD...")
    blog_items, howto_items = load_and_compile_all()
    print(f"[SYS // STATUS] COMPLETE // Site synchronized without '{slug}'.")
    return True

# --- Local HTTP Server ---
def serve_site(port=8080):
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    if not OUTPUT_DIR.exists() or not (OUTPUT_DIR / "index.html").exists():
        print(f"[SYS // SERVER] public/ directory not found or empty. Rebuilding site first...")
        load_and_compile_all()
    os.chdir(OUTPUT_DIR)
    print("\n" + "=" * 65)
    print(f" [TACTICAL HUD // LOCAL PREVIEW SERVER]")
    print(f"  Root:     {OUTPUT_DIR}")
    print(f"  URL:      http://localhost:{port}/")
    print(f"  Status:   Listening... (Press Ctrl+C to terminate)")
    print("=" * 65 + "\n")
    server = HTTPServer(('127.0.0.1', port), SimpleHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SYS // SERVER] Server stopped.")

# --- Main Entry Point ---
def main():
    parser = argparse.ArgumentParser(
        description="Tactical Dark // Zero-Dependency Site Publisher & Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 publish.py articol-nou.md
  python3 publish.py articol-nou.md --category howto
  python3 publish.py --rebuild
  python3 publish.py --delete compensare
  python3 publish.py --new "Cum am configurat FreeBSD" --category howto
  python3 publish.py --serve 8080
        """
    )
    parser.add_argument("file", nargs="?", help="Path to markdown file to ingest and publish")
    parser.add_argument("--category", "-c", choices=["blog", "howto", "programe"], help="Force specific category")
    parser.add_argument("--rebuild", "-r", action="store_true", help="Rebuild entire site from content/ directory")
    parser.add_argument("--delete", "--remove", "-d", metavar="SLUG", help="Delete an article (.md and HTML) and rebuild the site")
    parser.add_argument("--new", "-n", metavar="TITLE", help="Scaffold a new draft markdown template")
    parser.add_argument("--tag", "-t", help="Tag for the new scaffolded draft")
    parser.add_argument("--serve", "-s", nargs="?", const=8080, type=int, help="Start local web server (default port: 8080)")

    args = parser.parse_args()

    if args.serve:
        serve_site(args.serve)
        return

    if args.delete:
        delete_article(args.delete, forced_category=args.category)
        return

    if args.new:
        cat = args.category or "blog"
        scaffold_draft(args.new, category=cat, tag=args.tag)
        return

    if args.file:
        publish_markdown_file(args.file, forced_category=args.category)
        return

    # Default action: Rebuild all
    print("[SYS // REBUILD] Rebuilding entire site from content/ directory...")
    blog_items, howto_items = load_and_compile_all()
    print(f"[SYS // STATUS] COMPLETE // {len(blog_items)} blog posts & {len(howto_items)} howto guides compiled.")

if __name__ == "__main__":
    main()
