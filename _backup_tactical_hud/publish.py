#!/usr/bin/env python3
"""
=============================================================================
TACTICAL DARK // SITE PUBLISHER & GENERATOR
Dragoș Iorgulescu - Standalone Zero-Dependency Publishing System
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

# =============================================================================
# SITE GLOBAL CONFIGURATION
# Configurare centralizată: modifică aici titlul, subtitlul, autorul etc.
# Modificările de aici se propagă automat pe toate paginile la rularea scriptului.
# =============================================================================
SITE_CONFIG = {
    "author": "Dragoș Iorgulescu",
    "handle": "// DRAGOȘ IORGULESCU",
    "subtitle": "TEST ENGINEER // STRENGTH PRACTITIONER // ASPIRING VIDEOGRAPHER",
    "location": "BASE // BUCHAREST, RO",
    "site_title_suffix": "Tactical Dark HUD",
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

  <!-- Google Fonts: Space Grotesk, JetBrains Mono, Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Phosphor Icons -->
  <script src="https://unpkg.com/@phosphor-icons/web"></script>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            canvas: '#0B0F17',
            panel: 'rgba(17, 24, 39, 0.88)',
            'panel-solid': '#111827',
            recessed: '#0B0F17',
            borderline: '#1E293B',
          }},
          fontFamily: {{
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
            display: ['Space Grotesk', 'sans-serif'],
          }}
        }}
      }}
    }}
  </script>
  
  <!-- Tactical Design System -->
  <link rel="stylesheet" href="{root_path}css/tactical.css">
</head>
<body class="bg-[#0B0F17] text-slate-300 font-sans antialiased selection:bg-emerald-500/30 selection:text-white">
"""

def get_header(active_nav="", depth=0):
    root_path = "./" if depth == 0 else "../" * depth
    
    def active_cls(nav_name):
        if nav_name == active_nav:
            return "bg-slate-800 text-white border-slate-700 font-bold"
        return "text-slate-300 hover:text-white hover:bg-slate-800/60 border-transparent hover:border-slate-700"

    now_active_style = "ring-1 ring-emerald-400 bg-emerald-500/30" if active_nav == "now" else ""

    return f"""
  <!-- TOP HUD BAR -->
  <div class="border-b border-slate-800/80 bg-[#0B0F17]/95 text-[11px] font-mono text-slate-400 py-1.5 px-4 sm:px-8">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center gap-1.5 text-emerald-400 font-semibold">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          SYS // ONLINE
        </span>
        <span class="text-slate-700">|</span>
        <span class="text-slate-400">NODE // BUCHAREST</span>
        <span class="hidden sm:inline text-slate-700">|</span>
        <span class="hidden sm:inline text-slate-400">ARCH // STANDALONE-HTML5</span>
      </div>
      <div class="flex items-center gap-3 text-slate-400">
        <span id="hud-clock">--:--:-- // LOCAL</span>
        <span class="text-slate-700">|</span>
        <span class="text-sky-400 font-medium">ENGINE // ZERO DEPENDENCY</span>
        <span class="hidden sm:inline text-slate-700">|</span>
        <span id="theme-status-hud" class="hidden sm:inline font-mono text-[10px] uppercase text-emerald-400">MODE // DARK</span>
      </div>
    </div>
  </div>

  <!-- MAIN TACTICAL NAVBAR -->
  <header class="sticky top-0 z-50 backdrop-blur-xl bg-[#111827]/85 border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-8 h-16 flex items-center justify-between">
      <a href="{root_path}" class="flex items-center gap-3 group">
        <div class="w-9 h-9 rounded-xl bg-slate-900 border border-slate-700/80 flex items-center justify-center text-emerald-400 group-hover:border-emerald-500/50 group-hover:shadow-[0_0_15px_-3px_rgba(16,185,129,0.3)] transition-all">
          <i class="ph-duotone ph-terminal-window text-xl"></i>
        </div>
        <div>
          <div class="font-display font-bold text-slate-100 text-base tracking-wider group-hover:text-emerald-400 transition-colors">
            {SITE_CONFIG["handle"]}
          </div>
          <div class="text-[10px] font-mono uppercase tracking-widest text-slate-400">
            {SITE_CONFIG["subtitle"]}
          </div>
        </div>
      </a>

      <!-- DESKTOP NAV -->
      <nav class="hidden md:flex items-center gap-1 font-mono text-xs uppercase tracking-wider">
        <a href="{root_path}blog/" class="px-3 py-1.5 rounded-lg border transition-all {active_cls('blog')}">
          <span class="text-slate-500 mr-1">01 //</span>BLOG
        </a>
        <a href="{root_path}programe/" class="px-3 py-1.5 rounded-lg border transition-all {active_cls('programe')}">
          <span class="text-slate-500 mr-1">02 //</span>PROGRAMS
        </a>
        <a href="{root_path}sounds/" class="px-3 py-1.5 rounded-lg border transition-all {active_cls('sounds')}">
          <span class="text-slate-500 mr-1">03 //</span>SOUNDS
        </a>
        <a href="{root_path}howto/" class="px-3 py-1.5 rounded-lg border transition-all {active_cls('howto')}">
          <span class="text-slate-500 mr-1">04 //</span>HOW-TO
        </a>
        <a href="{root_path}now.html" class="ml-2 px-3 py-1.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/25 transition-all flex items-center gap-1.5 text-[11px] {now_active_style}">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
          NOW
        </a>

        <!-- THEME TOGGLE BUTTON (DESKTOP) -->
        <button type="button" class="theme-toggle-btn ml-3 w-9 h-9 rounded-xl bg-slate-900 border border-slate-700/80 flex items-center justify-center text-slate-300 hover:text-amber-400 hover:border-amber-500/50 transition-all cursor-pointer shadow-sm" title="Comută Schema de Culoare (Dark/Light)" aria-label="Comută Schema de Culoare">
          <i class="theme-toggle-icon ph-bold ph-sun text-base text-amber-400"></i>
        </button>
      </nav>

      <!-- MOBILE ACTIONS (THEME TOGGLE + HAMBURGER) -->
      <div class="flex items-center gap-2 md:hidden">
        <button type="button" class="theme-toggle-btn w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300 hover:text-amber-400 hover:border-amber-500/50 transition-all cursor-pointer shadow-sm" title="Comută Schema de Culoare" aria-label="Comută Schema de Culoare">
          <i class="theme-toggle-icon ph-bold ph-sun text-lg text-amber-400"></i>
        </button>
        <button id="mobile-menu-btn" class="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300 hover:text-white hover:border-slate-700" aria-label="Toggle Menu">
          <i class="ph-bold ph-list text-xl"></i>
        </button>
      </div>
    </div>

    <!-- MOBILE MENU DROPDOWN -->
    <div id="mobile-menu" class="hidden md:hidden border-t border-slate-800 bg-[#0B0F17]/98 backdrop-blur-xl px-4 py-4 space-y-2 font-mono text-xs uppercase tracking-wider">
      <a href="{root_path}" class="block px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 border border-transparent hover:border-slate-700">00 // HOME</a>
      <a href="{root_path}blog/" class="block px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 border border-transparent hover:border-slate-700">01 // BLOG</a>
      <a href="{root_path}programe/" class="block px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 border border-transparent hover:border-slate-700">02 // TRAINING PROGRAMS</a>
      <a href="{root_path}sounds/" class="block px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 border border-transparent hover:border-slate-700">03 // SOUNDS</a>
      <a href="{root_path}howto/" class="block px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-800 border border-transparent hover:border-slate-700">04 // HOW-TO</a>
      <a href="{root_path}now.html" class="block px-3 py-2.5 rounded-lg text-emerald-400 bg-emerald-500/10 border border-emerald-500/30">05 // NOW PAGE</a>
      <div class="pt-2 border-t border-slate-800 flex items-center justify-between px-3 py-2 text-slate-400">
        <span>SCHEMA VIZUALĂ</span>
        <button type="button" class="theme-toggle-btn px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 flex items-center gap-1.5">
          <i class="theme-toggle-icon ph-bold ph-sun text-amber-400"></i>
          <span>SCHIMBĂ TEMA</span>
        </button>
      </div>
    </div>
  </header>
"""

def get_footer(depth=0):
    root_path = "./" if depth == 0 else "../" * depth
    return f"""
  <!-- TACTICAL FOOTER HUD -->
  <footer class="mt-20 border-t border-slate-800/80 bg-[#0B0F17] py-12 px-4 sm:px-8">
    <div class="max-w-7xl mx-auto">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-8 mb-12">
        <div class="md:col-span-5 space-y-3">
          <div class="font-display font-bold text-slate-100 text-lg tracking-wider">
            // DRAGOȘ IORGULESCU
          </div>
          <p class="text-sm text-slate-400 font-sans leading-relaxed max-w-md">
            Software Test Engineer, kettlebell lifter, open-source enthusiast, and audio explorer. Dedicated to high-leverage simplicity, robust physical conditioning, and pragmatic engineering across open and proprietary platforms.
          </p>
          <div class="pt-2 flex flex-wrap items-center gap-2 text-xs font-mono text-slate-500">
            <span class="inline-flex items-center gap-1.5 text-emerald-400">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              STANDALONE ARCHITECTURE
            </span>
            <span class="text-slate-700">//</span>
            <span>100% PURE HTML5</span>
          </div>
        </div>

        <div class="md:col-span-3 space-y-3 font-mono text-xs">
          <div class="text-[11px] uppercase tracking-wider text-slate-400 font-bold">DIRECTORY //</div>
          <ul class="space-y-2">
            <li><a href="{root_path}blog/" class="text-slate-400 hover:text-emerald-400 transition-colors">01 // Journal (Blog)</a></li>
            <li><a href="{root_path}programe/" class="text-slate-400 hover:text-emerald-400 transition-colors">02 // Training Frameworks</a></li>
            <li><a href="{root_path}sounds/" class="text-slate-400 hover:text-emerald-400 transition-colors">03 // Sound Archives</a></li>
            <li><a href="{root_path}howto/" class="text-slate-400 hover:text-emerald-400 transition-colors">04 // Technical How-Tos</a></li>
            <li><a href="{root_path}now.html" class="text-slate-400 hover:text-emerald-400 transition-colors">05 // Current Focus (Now)</a></li>
          </ul>
        </div>

        <div class="md:col-span-4 space-y-3">
          <div class="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold">COMMS CHANNELS //</div>
          <div class="grid grid-cols-2 gap-2 text-xs font-mono">
            <a href="mailto:dragos@iorgos.net" class="flex items-center gap-2 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 hover:text-emerald-400 hover:border-emerald-500/40 transition-all">
              <i class="ph-bold ph-envelope text-base text-emerald-400"></i>
              <span>Email</span>
            </a>
            <a rel="me" href="https://mastodon.social/@diorgulescu" target="_blank" class="flex items-center gap-2 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 hover:text-purple-400 hover:border-purple-500/40 transition-all">
              <i class="ph-bold ph-chats text-base text-purple-400"></i>
              <span>Mastodon</span>
            </a>
            <a href="https://github.com/diorgulescu" target="_blank" class="flex items-center gap-2 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 hover:text-sky-400 hover:border-sky-500/40 transition-all">
              <i class="ph-bold ph-github-logo text-base text-sky-400"></i>
              <span>GitHub</span>
            </a>
            <a href="#" class="flex items-center gap-2 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-300 hover:text-amber-400 hover:border-amber-500/40 transition-all">
              <i class="ph-bold ph-terminal text-base text-amber-400"></i>
              <span>twtxt</span>
            </a>
          </div>
          <p class="text-[11px] font-mono text-slate-500 pt-1">
            LIFT HEAVY. BE KIND. BUILD ROBUST SOFTWARE.
          </p>
        </div>
      </div>

      <div class="pt-8 border-t border-slate-800/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-500">
        <div>
          &copy; <span id="current-year">2026</span> DRAGOȘ IORGULESCU. 
          <span class="text-slate-600">//</span> ALL RIGHTS RESERVED.
        </div>
        <div class="flex items-center gap-4">
          <span>HOST // <a href="https://my.namebox.ro/aff.php?aff=505" class="text-slate-400 hover:underline">NAMEBOX.RO</a></span>
          <span class="text-slate-600">|</span>
          <span class="text-emerald-400/90 font-semibold">ZERO ENGINE DEPENDENCY</span>
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
    target_dir = BASE_DIR / category / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    title = meta.get("title", slug.capitalize())
    date_iso = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
    date_display = format_display_date(date_iso)
    tag = meta.get("tag", f"{category.upper()} // DISPATCH")
    badge_cls = meta.get("badge_class", "badge-emerald" if category == "blog" else "badge-sky")
    read_time = meta.get("read_time", "5 MIN READ")

    content_clean = clean_content_paths(content_html, depth=2)

    page_html = f"""{get_html_head(f"{title} // {category.capitalize()}", depth=2)}
{get_header(active_nav=category, depth=2)}

<main class="max-w-4xl mx-auto px-4 sm:px-6 py-10">
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="../../{category}/" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-emerald-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO {category.upper()} DIRECTORY</span>
    </a>
    <div class="flex items-center gap-2">
      <span class="{badge_cls}">{tag}</span>
      <span class="status-pill">
        <span class="status-dot-emerald"></span>
        DISPATCH #{slug.upper()[:12]}
      </span>
    </div>
  </div>

  <div class="tactical-card mb-8">
    <div class="flex flex-wrap items-center gap-3 font-mono text-xs text-slate-400 mb-3">
      <span class="inline-flex items-center gap-1 text-emerald-400 font-semibold">
        <i class="ph-bold ph-calendar-blank"></i>
        <time datetime="{date_iso}">{date_display}</time>
      </span>
      <span class="text-slate-700">•</span>
      <span class="inline-flex items-center gap-1 text-sky-400">
        <i class="ph-bold ph-clock"></i>
        {read_time}
      </span>
      <span class="text-slate-700">•</span>
      <span class="text-slate-400">LOG // {slug}</span>
    </div>

    <h1 class="font-display font-bold text-2xl sm:text-4xl text-slate-100 leading-tight mb-4">
      {title}
    </h1>

    <div class="recessed-box text-xs font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
      <span>AUTHOR // DRAGOȘ IORGULESCU</span>
      <span>STREAM // {category.upper()}</span>
      <span>STATUS // PUBLISHED</span>
    </div>
  </div>

  <article class="tactical-panel p-6 sm:p-10 prose-tactical">
    {content_clean}
  </article>

  <div class="mt-8 flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-[#111827]/60">
    <a href="../../{category}/" class="tactical-btn">
      <i class="ph-bold ph-arrow-left"></i>
      BACK TO ALL {category.upper()}
    </a>
    <a href="#" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;" class="tactical-btn-emerald">
      <i class="ph-bold ph-arrow-up"></i>
      BACK TO TOP
    </a>
  </div>
</main>

{get_footer(depth=2)}"""

    with open(target_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(page_html)

# --- Category Index Generator ---
def generate_category_index(category, items):
    output_dir = BASE_DIR / category
    output_dir.mkdir(parents=True, exist_ok=True)

    category_titles = {
        "blog": "Journal & Thoughts",
        "howto": "Technical How-Tos",
        "programe": "Training Frameworks"
    }
    category_streams = {
        "blog": "STREAM 01 // WRITTEN ESSAYS & NOTES",
        "howto": "STREAM 04 // STEP-BY-STEP ENGINEERING PROTOCOLS",
        "programe": "STREAM 02 // CONDITIONING & PHYSICAL PREPARATION"
    }

    cards_html = ""
    for item in items:
        badge_cls = item.get("badge_class", "badge-emerald" if category == "blog" else "badge-sky")
        tag = item.get("tag", f"{category.upper()} // ARTICLE")
        date_display = item.get("date_display", item.get("date", ""))
        read_time = item.get("read_time", "5 MIN READ")
        title = item.get("title", item["slug"].capitalize())
        excerpt = item.get("excerpt", "")

        glow_cls = "glow-emerald" if category == "blog" else "glow-sky"
        action_text = "READ COMPLETE DISPATCH" if category == "blog" else "OPEN PROTOCOL MANUAL"
        accent_color = "text-emerald-400" if category == "blog" else "text-sky-400"

        cards_html += f"""
        <article class="tactical-card {glow_cls} group journal-entry">
          <div class="flex flex-wrap items-center justify-between gap-2 mb-3 font-mono text-xs">
            <div class="flex items-center gap-2">
              <span class="{badge_cls}">{tag}</span>
              <span class="text-slate-500">•</span>
              <span class="{accent_color} font-semibold">{date_display}</span>
            </div>
            <span class="text-slate-400 text-[11px]">{read_time}</span>
          </div>

          <h2 class="font-display font-bold text-xl text-slate-100 group-hover:{accent_color} transition-colors mb-2">
            <a href="{item['slug']}/" class="hover:underline underline-offset-4">
              {title}
            </a>
          </h2>

          <p class="text-sm text-slate-400 font-sans leading-relaxed mb-4">
            {excerpt}
          </p>

          <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between font-mono text-xs">
            <a href="{item['slug']}/" class="inline-flex items-center gap-1.5 {accent_color} hover:underline font-semibold">
              {action_text}
              <i class="ph-bold ph-arrow-right text-sm group-hover:translate-x-1 transition-transform"></i>
            </a>
            <span class="text-slate-400 uppercase text-[10px]">LOG // {item['slug'][:15]}</span>
          </div>
        </article>
        """

    cat_title = category_titles.get(category, category.capitalize())
    cat_stream = category_streams.get(category, f"STREAM // {category.upper()}")

    page_html = f"""{get_html_head(f"{cat_title} // Directory", depth=1)}
{get_header(active_nav=category, depth=1)}

<main class="max-w-7xl mx-auto px-4 sm:px-8 py-10">
  <div class="tactical-panel p-6 sm:p-8 mb-10">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
      <div>
        <div class="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-emerald-400 mb-1">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          {cat_stream}
        </div>
        <h1 class="font-display font-bold text-3xl sm:text-4xl text-slate-100 tracking-tight">
          {cat_title}
        </h1>
      </div>
      <div class="recessed-box font-mono text-xs text-slate-400 flex items-center gap-3">
        <span>TOTAL ENTRIES: <strong class="text-emerald-400 font-bold">{len(items)}</strong></span>
        <span class="text-slate-700">|</span>
        <span>INDEX // CHRONOLOGICAL</span>
      </div>
    </div>
    <p class="text-slate-400 text-sm max-w-3xl leading-relaxed">
      Curated dispatches, technical documentations, and engineering notes.
    </p>

    <!-- Live Client Filter -->
    <div class="mt-6 flex items-center gap-3">
      <div class="relative flex-1 max-w-md">
        <i class="ph-bold ph-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm"></i>
        <input 
          id="hud-filter-input"
          data-target=".journal-entry"
          type="text" 
          placeholder="FILTER {category.upper()} BY KEYWORD..." 
          class="w-full pl-9 pr-4 py-2 rounded-xl bg-[#0B0F17] border border-slate-800 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500/60 transition-colors"
        >
      </div>
      <span class="text-xs font-mono text-slate-400 hidden sm:inline">LIVE FILTER HUD</span>
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {cards_html}
  </div>
</main>

{get_footer(depth=1)}"""

    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(page_html)

# --- Home Page Generator ---
def generate_home_page(posts, guides):
    # Top 3 latest blog posts
    recent_posts_html = ""
    for p in posts[:3]:
        badge_cls = p.get("badge_class", "badge-emerald")
        tag_short = p.get("tag", "BLOG").split("//")[0].strip()
        recent_posts_html += f"""
        <div class="p-4 rounded-xl bg-[#0B0F17] border border-slate-800 hover:border-slate-700 transition-all group">
          <div class="flex items-center justify-between text-xs font-mono mb-1.5">
            <span class="{badge_cls} text-[10px] py-0.5">{tag_short}</span>
            <span class="text-slate-500">{p.get('date_display', p.get('date', ''))}</span>
          </div>
          <h3 class="font-display font-bold text-base text-slate-100 group-hover:text-emerald-400 transition-colors">
            <a href="blog/{p['slug']}/">{p['title']}</a>
          </h3>
          <p class="text-xs text-slate-400 font-sans mt-1 line-clamp-2">
            {p.get('excerpt', '')}
          </p>
        </div>
        """

    # Top 3 latest guides
    recent_guides_html = ""
    for g in guides[:3]:
        badge_cls = g.get("badge_class", "badge-sky")
        tag_short = g.get("tag", "HOWTO").split("//")[0].strip()
        recent_guides_html += f"""
        <div class="p-4 rounded-xl bg-[#0B0F17] border border-slate-800 hover:border-slate-700 transition-all group">
          <div class="flex items-center justify-between text-xs font-mono mb-1.5">
            <span class="{badge_cls} text-[10px] py-0.5">{tag_short}</span>
            <span class="text-slate-500">{g.get('date', '')}</span>
          </div>
          <h3 class="font-display font-bold text-base text-slate-100 group-hover:text-sky-400 transition-colors">
            <a href="howto/{g['slug']}/">{g['title']}</a>
          </h3>
          <p class="text-xs text-slate-400 font-sans mt-1 line-clamp-2">
            {g.get('excerpt', '')}
          </p>
        </div>
        """

    home_html = f"""{get_html_head("Dragoș Iorgulescu // Tactical Dark HUD", depth=0)}
{get_header(depth=0)}

<main class="max-w-7xl mx-auto px-4 sm:px-8 py-8 sm:py-12">
  <div class="grid grid-cols-1 md:grid-cols-12 gap-6">

    <!-- HERO BENTO CARD (8 cols) -->
    <div class="md:col-span-8 tactical-card glow-emerald flex flex-col justify-between">
      <div>
        <div class="flex flex-wrap items-center gap-3 font-mono text-xs text-slate-400 mb-4">
          <span class="badge-emerald">STATUS // ACTIVE</span>
          <span class="text-slate-600">•</span>
          <span class="text-slate-400">BASE // BUCHAREST, RO</span>
        </div>

        <h1 class="font-display font-bold text-3xl sm:text-5xl text-slate-100 tracking-tight leading-tight mb-4">
          Dragoș Iorgulescu
        </h1>

        <p class="text-lg text-slate-300 font-sans leading-relaxed mb-4 max-w-2xl">
          Husband, father of two boys. Software Test Engineer, kettlebell lifter, and open-source enthusiast. Dedicated to minimal tools, robust physical conditioning, and honest engineering.
        </p>

        <p class="text-sm text-slate-400 font-sans leading-relaxed mb-6 max-w-2xl">
          Check out <a href="now.html" class="text-emerald-400 hover:text-emerald-300 font-semibold underline underline-offset-4">my "now" page</a> to see what I'm currently up to in real-time.
        </p>
      </div>

      <div class="pt-6 border-t border-slate-800 flex flex-wrap items-center gap-3">
        <a href="programe/" class="tactical-btn-emerald">
          <i class="ph-bold ph-barbell text-base"></i>
          TRAINING PROGRAMS
        </a>
        <a href="blog/" class="tactical-btn">
          <i class="ph-bold ph-book-open text-base"></i>
          JOURNAL DISPATCHES
        </a>
        <a href="howto/" class="tactical-btn">
          <i class="ph-bold ph-terminal text-base"></i>
          HOW-TO MANUALS
        </a>
      </div>
    </div>

    <!-- SYSTEM KPI HUD (4 cols) -->
    <div class="md:col-span-4 tactical-card flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between text-xs font-mono text-slate-400 mb-4">
          <span class="uppercase tracking-wider">SYSTEM KPI HUD</span>
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        </div>

        <div class="grid grid-cols-2 gap-3 font-mono">
          <div class="recessed-box">
            <span class="text-2xl font-bold text-slate-100 font-mono block">{len(posts):02d}</span>
            <span class="text-[10px] uppercase text-emerald-400 tracking-wider">DISPATCHES</span>
          </div>
          <div class="recessed-box">
            <span class="text-2xl font-bold text-slate-100 font-mono block">{len(guides):02d}</span>
            <span class="text-[10px] uppercase text-sky-400 tracking-wider">HOW-TO GUIDES</span>
          </div>
          <div class="recessed-box">
            <span class="text-2xl font-bold text-slate-100 font-mono block">03</span>
            <span class="text-[10px] uppercase text-amber-400 tracking-wider">FRAMEWORKS</span>
          </div>
          <div class="recessed-box">
            <span class="text-2xl font-bold text-slate-100 font-mono block">05</span>
            <span class="text-[10px] uppercase text-purple-400 tracking-wider">AUDIO RELEASES</span>
          </div>
        </div>

        <div class="mt-4 recessed-box text-xs font-mono text-slate-400 space-y-1">
          <div class="flex justify-between">
            <span>ENGINE:</span>
            <strong class="text-emerald-400">0% ENGINE (PURE HTML)</strong>
          </div>
          <div class="flex justify-between">
            <span>UPTIME:</span>
            <strong class="text-slate-200">99.99% STATIC</strong>
          </div>
          <div class="flex justify-between">
            <span>TOOLING:</span>
            <strong class="text-slate-200">TAILWIND + PHOSPHOR</strong>
          </div>
        </div>
      </div>

      <div class="pt-4 border-t border-slate-800 text-xs font-mono text-slate-500 flex items-center justify-between">
        <span>SECURITY // STATIC</span>
        <span class="text-emerald-400 font-semibold">ALL CLEAR</span>
      </div>
    </div>

    <!-- TRAINING FRAMEWORKS SECTION (12 cols) -->
    <div class="md:col-span-12">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <h2 class="font-display font-bold text-2xl text-slate-100">
            Training & Conditioning
          </h2>
        </div>
        <a href="programe/" class="font-mono text-xs text-emerald-400 hover:underline">
          ALL FRAMEWORKS &rarr;
        </a>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="tactical-card glow-emerald flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="badge-emerald">STRENGTH & HYPERTROPHY</span>
              <span class="text-xs font-mono text-slate-400">01</span>
            </div>
            <h3 class="font-display font-bold text-xl text-slate-100 mb-2">
              <a href="programe/tension-spectrum/" class="hover:text-emerald-400 transition-colors">Tension Spectrum</a>
            </h3>
            <p class="text-sm text-slate-400 font-sans leading-relaxed mb-4">
              A structured training program focused on functional strength and hypertrophy through specific kettlebell complexes and loaded stretching.
            </p>
          </div>
          <a href="programe/tension-spectrum/" class="tactical-btn-emerald text-center">
            VIEW PROTOCOL
          </a>
        </div>

        <div class="tactical-card glow-amber flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="badge-amber">STRONGFIRST CERT</span>
              <span class="text-xs font-mono text-slate-400">02</span>
            </div>
            <h3 class="font-display font-bold text-xl text-slate-100 mb-2">
              <a href="programe/sfg-prep/" class="hover:text-amber-400 transition-colors">SFG I & SFB Prep</a>
            </h3>
            <p class="text-sm text-slate-400 font-sans leading-relaxed mb-4">
              Comprehensive 3-phase training progression for StrongFirst Girya Level 1 and StrongFirst Bodyweight certifications.
            </p>
          </div>
          <a href="programe/sfg-prep/" class="tactical-btn text-center hover:border-amber-500/50 hover:text-amber-400">
            VIEW BLUEPRINT
          </a>
        </div>

        <div class="tactical-card glow-purple flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="badge-purple">REHAB & AEROBIC BASE</span>
              <span class="text-xs font-mono text-slate-400">03</span>
            </div>
            <h3 class="font-display font-bold text-xl text-slate-100 mb-2">
              <a href="programe/bjj-prep/" class="hover:text-purple-400 transition-colors">BJJ Prep & Reabilitare</a>
            </h3>
            <p class="text-sm text-slate-400 font-sans leading-relaxed mb-4">
              Elbow tendonitis rehabilitation, daily micro-routine, Zone 2 mitochondrial conditioning, and Brazilian Jiu-Jitsu ground mobility.
            </p>
          </div>
          <a href="programe/bjj-prep/" class="tactical-btn text-center hover:border-purple-500/50 hover:text-purple-400">
            VIEW PROTOCOL
          </a>
        </div>
      </div>
    </div>

    <!-- TECH INTERESTS & PROJECTS (7 cols) -->
    <div class="md:col-span-7 tactical-card">
      <div class="flex items-center gap-2 mb-4">
        <span class="badge-sky">ENGINEERING // CRAFT</span>
        <h2 class="font-display font-bold text-xl text-slate-100">
          Projects & Interests
        </h2>
      </div>

      <div class="space-y-4 text-sm font-sans">
        <div class="recessed-box">
          <div class="flex items-center justify-between mb-1 font-mono text-xs">
            <strong class="text-emerald-400">DAMF // Device Automation & Management</strong>
            <a href="https://github.com/diorgulescu/DAMF" target="_blank" class="text-slate-400 hover:text-white">
              <i class="ph-bold ph-github-logo text-sm"></i>
            </a>
          </div>
          <p class="text-slate-300 text-xs leading-relaxed">
            Free & open framework for software test engineers and lab maintainers to manage embedded devices, hardware boards & prototypes while running automated test suites and generating structured test reports.
          </p>
        </div>

        <div class="recessed-box">
          <div class="flex items-center justify-between mb-1 font-mono text-xs">
            <strong class="text-sky-400">Suckless Ubuntu // Minimal Linux Workflow</strong>
            <a href="https://github.com/diorgulescu/suckless-ubuntu" target="_blank" class="text-slate-400 hover:text-white">
              <i class="ph-bold ph-github-logo text-sm"></i>
            </a>
          </div>
          <p class="text-slate-300 text-xs leading-relaxed">
            A tailored Linux configuration based on suckless.org tools (dwm, dmenu, slstatus, surf) engineered for maximum speed, zero distraction, and full keyboard navigation.
          </p>
        </div>

        <div class="pt-2 text-xs text-slate-400 leading-relaxed font-mono">
          <span class="text-slate-300 font-bold">OTHER PURSUITS:</span>
          Bicycle touring (<a href="https://www.verdaspirito.org" class="text-sky-400 hover:underline">verdaspirito.org</a>), ThinkPads, LaTeX, static architectures, amateur trainspotting.
        </div>
      </div>
    </div>

    <!-- SOUNDS PREVIEW (5 cols) -->
    <div class="md:col-span-5 tactical-card flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-3">
          <span class="badge-purple">AUDIO EXPLORATION</span>
          <span class="text-xs font-mono text-slate-400">STREAM 03</span>
        </div>
        <h2 class="font-display font-bold text-xl text-slate-100 mb-2">
          Sounds & Synthesizers
        </h2>
        <p class="text-sm text-slate-400 font-sans leading-relaxed mb-4">
          Played bass guitar, drums, and synthesizers over the years, ranging from drone rock to ambient soundscapes and field recordings.
        </p>

        <div class="space-y-2 font-mono text-xs">
          <div class="flex items-center justify-between p-2 rounded-lg bg-[#0B0F17] border border-slate-800">
            <span class="text-slate-200">Scentient Pencils</span>
            <span class="text-purple-400">Ambient / Modular</span>
          </div>
          <div class="flex items-center justify-between p-2 rounded-lg bg-[#0B0F17] border border-slate-800">
            <span class="text-slate-200">Sentem</span>
            <span class="text-amber-400">Drone Rock / Metal</span>
          </div>
        </div>
      </div>

      <div class="pt-4 border-t border-slate-800">
        <a href="sounds/" class="tactical-btn w-full text-center hover:border-purple-500/50 hover:text-purple-400">
          EXPLORE AUDIO ARCHIVE
          <i class="ph-bold ph-arrow-right"></i>
        </a>
      </div>
    </div>

    <!-- RECENT BLOG POSTS (6 cols) -->
    <div class="md:col-span-6 tactical-card">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <h2 class="font-display font-bold text-xl text-slate-100">
            Recent Dispatches
          </h2>
        </div>
        <a href="blog/" class="font-mono text-xs text-emerald-400 hover:underline">
          ALL DISPATCHES &rarr;
        </a>
      </div>
      <div class="space-y-3">
        {recent_posts_html}
      </div>
    </div>

    <!-- RECENT HOWTOS (6 cols) -->
    <div class="md:col-span-6 tactical-card">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-sky-400"></span>
          <h2 class="font-display font-bold text-xl text-slate-100">
            Technical How-Tos
          </h2>
        </div>
        <a href="howto/" class="font-mono text-xs text-sky-400 hover:underline">
          ALL HOW-TOS &rarr;
        </a>
      </div>
      <div class="space-y-3">
        {recent_guides_html}
      </div>
    </div>

  </div>
</main>

{get_footer(depth=0)}"""

    with open(BASE_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(home_html)

# --- Core Scanner & Rebuilder ---
def load_and_compile_all():
    content_dir = BASE_DIR / "content"
    if not content_dir.exists():
        print(f"[ERR // CONTENT] content/ directory not found at {content_dir}")
        return [], []

    blog_items = []
    howto_items = []

    # 1. Process Blog
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
                draft_dir = BASE_DIR / "blog" / slug
                if draft_dir.is_dir():
                    shutil.rmtree(draft_dir)
                    print(f"[SYS // DRAFT] Removed unlisted HTML directory for draft: blog/{slug}/")
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

    # Automatic cleanup of orphaned blog directories
    active_blog_slugs = {item["slug"] for item in blog_items}
    blog_root = BASE_DIR / "blog"
    if blog_root.exists():
        for sub in blog_root.iterdir():
            if sub.is_dir() and sub.name not in active_blog_slugs and not sub.name.startswith(("_", ".")):
                shutil.rmtree(sub)
                print(f"[SYS // CLEANUP] Removed orphaned article directory: blog/{sub.name}/")

    blog_items.sort(key=lambda x: str(x["date"]), reverse=True)
    generate_category_index("blog", blog_items)

    # 2. Process Howto
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
                draft_dir = BASE_DIR / "howto" / slug
                if draft_dir.is_dir():
                    shutil.rmtree(draft_dir)
                    print(f"[SYS // DRAFT] Removed unlisted HTML directory for draft: howto/{slug}/")
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

    # Automatic cleanup of orphaned howto directories
    active_howto_slugs = {item["slug"] for item in howto_items}
    howto_root = BASE_DIR / "howto"
    if howto_root.exists():
        for sub in howto_root.iterdir():
            if sub.is_dir() and sub.name not in active_howto_slugs and not sub.name.startswith(("_", ".")):
                shutil.rmtree(sub)
                print(f"[SYS // CLEANUP] Removed orphaned guide directory: howto/{sub.name}/")

    howto_items.sort(key=lambda x: str(x["date"]), reverse=True)
    generate_category_index("howto", howto_items)

    # 3. Rebuild Home Page
    generate_home_page(blog_items, howto_items)

    # 4. Synchronize static pages (now.html, programe/, sounds/, etc.)
    sync_static_headers()

    return blog_items, howto_items

def sync_static_headers():
    """
    Synchronizes SITE_CONFIG identity, theme switcher, and head scripts across all HTML files
    including standalone static pages (now.html, sounds/, programe/, kettlebell/).
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

    desktop_btn = """        <!-- THEME TOGGLE BUTTON (DESKTOP) -->
        <button type="button" class="theme-toggle-btn ml-3 w-9 h-9 rounded-xl bg-slate-900 border border-slate-700/80 flex items-center justify-center text-slate-300 hover:text-amber-400 hover:border-amber-500/50 transition-all cursor-pointer shadow-sm" title="Comută Schema de Culoare (Dark/Light)" aria-label="Comută Schema de Culoare">
          <i class="theme-toggle-icon ph-bold ph-sun text-base text-amber-400"></i>
        </button>
      </nav>"""

    mobile_actions = """      <!-- MOBILE ACTIONS (THEME TOGGLE + HAMBURGER) -->
      <div class="flex items-center gap-2 md:hidden">
        <button type="button" class="theme-toggle-btn w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300 hover:text-amber-400 hover:border-amber-500/50 transition-all cursor-pointer shadow-sm" title="Comută Schema de Culoare" aria-label="Comută Schema de Culoare">
          <i class="theme-toggle-icon ph-bold ph-sun text-lg text-amber-400"></i>
        </button>
        <button id="mobile-menu-btn" class="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300 hover:text-white hover:border-slate-700" aria-label="Toggle Menu">
          <i class="ph-bold ph-list text-xl"></i>
        </button>
      </div>"""

    for html_file in BASE_DIR.glob("**/*.html"):
        if "_legacy_hugo" in html_file.parts:
            continue
        try:
            content = html_file.read_text(encoding="utf-8")
            orig = content

            # 1. Update <html lang="ro" class="dark"> to <html lang="ro">
            content = re.sub(r'<html\s+lang="ro"\s+class="dark">', '<html lang="ro">', content)

            # 2. Add zero-fouc script if missing
            if "theme_preference" not in content and "</head>" in content:
                content = content.replace("</head>", f"{theme_script}\n</head>")

            # 3. Update subtitle & handle
            content = re.sub(
                r'(<div class="text-\[10px\] font-mono uppercase tracking-widest text-slate-400">\s*)(.*?)(\s*</div>)',
                rf'\g<1>{SITE_CONFIG["subtitle"]}\g<3>',
                content
            )
            content = re.sub(
                r'(<div class="font-display font-bold text-slate-100 text-base tracking-wider group-hover:text-emerald-400 transition-colors">\s*)(// [^\n<]+)(\s*</div>)',
                rf'\g<1>{SITE_CONFIG["handle"]}\g<3>',
                content
            )

            # 4. Add desktop theme toggle button if missing
            if 'theme-toggle-btn' not in content:
                if '</nav>' in content:
                    content = content.replace('</nav>', desktop_btn, 1)

                # Add mobile toggle button
                if '<button id="mobile-menu-btn"' in content and 'class="flex items-center gap-2 md:hidden"' not in content:
                    content = re.sub(
                        r'<!-- MOBILE HAMBURGER -->\s*<button id="mobile-menu-btn"[^>]*>[\s\S]*?</button>',
                        mobile_actions,
                        content
                    )
                # Add theme indicator if missing
                if 'theme-status-hud' not in content and 'theme-status-telemetry' not in content and 'ENGINE // ZERO DEPENDENCY</span>' in content:
                    content = content.replace(
                        'ENGINE // ZERO DEPENDENCY</span>',
                        'ENGINE // ZERO DEPENDENCY</span>\n        <span class="hidden sm:inline text-slate-700">|</span>\n        <span id="theme-status-hud" class="hidden sm:inline font-mono text-[10px] uppercase text-emerald-400">MODE // DARK</span>'
                    )

            # 5. Synchronize bio & motto (sovereignty softening)
            old_bio = "Software Test Engineer, kettlebell lifter, open-source proponent, and audio explorer. Dedicated to high-leverage simplicity, robust physical conditioning, and sovereign technology."
            new_bio = "Software Test Engineer, kettlebell lifter, open-source enthusiast, and audio explorer. Dedicated to high-leverage simplicity, robust physical conditioning, and pragmatic engineering across open and proprietary platforms."
            content = content.replace(old_bio, new_bio)

            old_motto = "LIFT HEAVY. BE KIND. BUILD SOVEREIGN SOFTWARE."
            new_motto = "LIFT HEAVY. BE KIND. BUILD ROBUST SOFTWARE."
            content = content.replace(old_motto, new_motto)

            # 6. Eliminate telemetry references from UI headers, badges, IDs & descriptions
            content = content.replace("OPERATING TELEMETRY // ACTIVE", "STATUS // ACTIVE")
            content = content.replace("NOW TELEMETRY &bull; WHAT I'M UP TO", "CURRENT FOCUS &bull; WHAT I'M UP TO")
            content = content.replace("Now // Current Telemetry", "Now // Current Focus")
            content = content.replace("FREQUENCY TELEMETRY // 2008 – PRESENT", "AUDIO ARCHIVE // 2008 – PRESENT")
            content = content.replace("7-DAY TELEMETRY", "7-DAY PROTOCOL")
            content = content.replace("Personal telemetry dashboard", "Personal website")
            content = content.replace("Tactical Dark Telemetry HUD", "Tactical Dark HUD")
            content = content.replace("<!-- TOP TELEMETRY HUD BAR -->", "<!-- TOP HUD BAR -->")
            content = content.replace("FORMAT // RAW TELEMETRY ESSAY", "FORMAT // RAW DISPATCH ESSAY")
            content = content.replace("<!-- TELEMETRY KPI HUD (4 cols) -->", "<!-- SYSTEM KPI HUD (4 cols) -->")
            content = content.replace("generating telemetry reports", "generating structured test reports")
            content = content.replace('id="telemetry-clock"', 'id="hud-clock"')
            content = content.replace('id="theme-status-telemetry"', 'id="theme-status-hud"')
            content = content.replace("<!-- Bottom Telemetry Bar -->", "<!-- Bottom Bar -->")
            content = content.replace("<!-- BREADCRUMB / HUD TELEMETRY -->", "<!-- BREADCRUMB / HUD -->")
            content = content.replace("<!-- PAGE HEADER & TELEMETRY -->", "<!-- PAGE HEADER & STATUS -->")

            if content != orig:
                html_file.write_text(content, encoding="utf-8")
        except Exception:
            pass

# --- Single File Ingest / Publishing ---
def publish_markdown_file(filepath, forced_category=None):
    p = Path(filepath)
    if not p.is_file():
        print(f"[ERR // FILE] File does not exist: {filepath}")
        sys.exit(1)

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
    print(f"[SYS // COMPILE] Compiling {category}/{slug}/index.html...")
    blog_items, howto_items = load_and_compile_all()

    print("\n" + "=" * 65)
    print(f" [TACTICAL HUD // PUBLISHED SUCCESSFULLY]")
    print(f"  Category:      {category.upper()}")
    print(f"  Title:         {title}")
    print(f"  Slug:          {slug}")
    print(f"  Date:          {meta['date']} ({format_display_date(meta['date'])})")
    print(f"  HTML URL:      {category}/{slug}/index.html")
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

        html_dir = BASE_DIR / cat / slug
        if html_dir.is_dir():
            shutil.rmtree(html_dir)
            print(f"[SYS // CLEANUP] Removed HTML directory: {cat}/{slug}/")
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
    os.chdir(BASE_DIR)
    print(f"[SYS // SERVER] Starting local Tactical HUD server on http://localhost:{port}...")
    print(f"[SYS // SERVER] Press Ctrl+C to terminate.")
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
