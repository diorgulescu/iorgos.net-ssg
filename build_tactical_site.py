#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TACTICAL DARK // BENTO HUD // STATIC SITE GENERATOR
Migrates iorgos-hugo to a 100% engine-free, pure HTML website.

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
"""

import os, re, glob, html
from pathlib import Path

BASE_DIR = Path("/Users/dragosiorgulescu/work/iorgos-hugo")

SITE_CONFIG = {
    "author": "Dragoș Iorgulescu",
    "handle": "// DRAGOȘ IORGULESCU",
    "subtitle": "TEST ENGINEER // STRENGTH PRACTITIONER // ASPIRING VIDEOGRAPHER",
}

# Common metadata for blog posts
BLOG_META = {
    "telefonul": {
        "tag": "SOCIETY // DIGITAL",
        "badge_class": "badge-emerald",
        "excerpt": "Telefonul a devenit o funcție minoră, pierdută printre multe altele mai frumos colorate și mai dătătoare de dependență. Un martor omniprezent al tuturor trăirilor intime.",
        "read_time": "5 MIN READ"
    },
    "pacaneaua-din-buzunar": {
        "tag": "ATTENTION // ADDICTION",
        "badge_class": "badge-amber",
        "excerpt": "Notificări, vibrații fantomă și dopamină facilă. Cum dispozitivele mobile au reproiectat reflexele umane în mecanisme de tip slot machine.",
        "read_time": "7 MIN READ"
    },
    "curatenie-reprezentata-femei": {
        "tag": "CULTURE // ADVERTISING",
        "badge_class": "badge-purple",
        "excerpt": "Despre stereotipuri, reclame la produse de curățenie și contrastul dintre realitatea brută a muncii casnice și idealizarea artificială.",
        "read_time": "6 MIN READ"
    },
    "soferi-grabiti-scaune-copii": {
        "tag": "SAFETY // PARENTING",
        "badge_class": "badge-amber",
        "excerpt": "Siguranța rutieră, importanța scaunelor auto rear-facing pentru copii și responsabilitatea adulților din spatele volanului.",
        "read_time": "11 MIN READ"
    },
    "compensare": {
        "tag": "TRAINING // RECOVERY",
        "badge_class": "badge-sky",
        "excerpt": "Gânduri scurte despre procesul de supracompensare, refacere celulară și asimilarea adaptărilor structurale post-antrenament.",
        "read_time": "1 MIN READ"
    },
    "tool-becomes-drug": {
        "tag": "ESSAY // MINIMALISM",
        "badge_class": "badge-emerald",
        "excerpt": "Imagine calling a plumber who falls in love with his wrench instead of fixing the pipe. An analogy on how smartphones shifted from tools into addictive traps.",
        "read_time": "6 MIN READ"
    },
    "gasit-nordul": {
        "tag": "EXPEDITION // CYCLING",
        "badge_class": "badge-sky",
        "excerpt": "O călătorie pe bicicletă către cel mai nordic punct al României (Horodiștea). Drumuri de țară, liniște, reflecții și redescoperirea ritmului propriu.",
        "read_time": "10 MIN READ"
    },
    "is-strava-another-facebook": {
        "tag": "FITNESS // PRIVACY",
        "badge_class": "badge-rose",
        "excerpt": "Does tracking every heartbeat and mile turn healthy physical training into another vanity validation loop? An inquiry into fitness telemetry vs social vanity.",
        "read_time": "5 MIN READ"
    }
}

# Common metadata for howto guides
HOWTO_META = {
    "deploy-hyperv2019": {
        "date": "2021-05-20",
        "tag": "WINDOWS SERVER // HYPER-V",
        "badge_class": "badge-sky",
        "excerpt": "Step-by-step deployment guide for Microsoft Hyper-V Server 2019 in a workgroup environment without a Domain Controller, managed via RSAT.",
        "read_time": "6 MIN READ"
    },
    "create-fixed-size-files": {
        "date": "2021-03-24",
        "tag": "LINUX & WINDOWS // QA AUTOMATION",
        "badge_class": "badge-emerald",
        "excerpt": "Techniques for software test engineers to instantly create pre-sized dummy files to simulate low disk conditions in automated testing suites.",
        "read_time": "3 MIN READ"
    },
    "aliases-profiles-pwsh": {
        "date": "2021-02-12",
        "tag": "POWERSHELL // CLI PRODUCTIVITY",
        "badge_class": "badge-amber",
        "excerpt": "Configuring PowerShell profiles to provide Unix-like aliases and functions for comfortable multi-OS terminal operations.",
        "read_time": "4 MIN READ"
    },
    "ssh-auth-windows10": {
        "date": "2020-11-01",
        "tag": "WINDOWS 10 // SSH SECURITY",
        "badge_class": "badge-purple",
        "excerpt": "A clean PowerShell one-liner to generate RSA key pairs and deploy them to remote Linux/Unix servers without ssh-copy-id.",
        "read_time": "2 MIN READ"
    },
    "first-homelab": {
        "date": "2020-06-10",
        "tag": "HARDWARE // HOMELAB",
        "badge_class": "badge-emerald",
        "excerpt": "Designing an unobtrusive, quiet homelab setup with Supermicro, Proxmox VE, pfSense routing, and mini-PCs inside home furniture.",
        "read_time": "5 MIN READ"
    },
    "first-raspberrypi-cluster": {
        "date": "2020-05-12",
        "tag": "ARM64 // KUBERNETES CLUSTERING",
        "badge_class": "badge-sky",
        "excerpt": "Building a low-power 4-node Raspberry Pi cluster for exploring Kubernetes (k3s), VMWare ESXi on ARM, and automated ATF test frameworks.",
        "read_time": "6 MIN READ"
    },
    "compiling-suckless-tools-freebsd": {
        "date": "2019-10-23",
        "tag": "FREEBSD // SUCKLESS C TOOLS",
        "badge_class": "badge-amber",
        "excerpt": "Compiling dwm, dmenu, slstatus, and surf from source on FreeBSD. Packages, Xorg configuration, C source customizations, and lightweight desktop workflow.",
        "read_time": "12 MIN READ"
    }
}

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
  
  <!-- Favicon -->
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
        <!-- Col 1: Identity & Motto -->
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

        <!-- Col 2: Navigation Directory -->
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

        <!-- Col 3: Direct Comms -->
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

      <!-- Bottom Bar -->
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

  <!-- Scripts -->
  <script src="{root_path}js/tactical.js"></script>
</body>
</html>
"""

def clean_content_html(content_html, depth=0):
    """Adjust image paths and clean obsolete attributes."""
    root_path = "./" if depth == 0 else "../" * depth
    # Replace root image links like /images/... with relative links {root_path}images/...
    cleaned = re.sub(r'src=["\']/images/(.*?)["\']', f'src="{root_path}images/\\1"', content_html)
    cleaned = re.sub(r'href=["\']/images/(.*?)["\']', f'href="{root_path}images/\\1"', cleaned)
    # Fix docs links
    cleaned = re.sub(r'href=["\']/docs/(.*?)["\']', f'href="{root_path}docs/\\1"', cleaned)
    return cleaned

# Generate Blog Posts
def generate_blog_posts():
    blog_dir = BASE_DIR / "public" / "blog"
    output_dir = BASE_DIR / "blog"
    output_dir.mkdir(exist_ok=True)
    
    posts_data = []

    for post_folder in sorted(blog_dir.glob("*/index.html")):
        slug = post_folder.parent.name
        with open(post_folder, "r", encoding="utf-8") as f:
            raw_html = f.read()

        title_match = re.search(r'<h1>(.*?)</h1>', raw_html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else slug.capitalize()
        
        date_match = re.search(r'<time datetime="(.*?)">(.*?)</time>', raw_html)
        date_iso = date_match.group(1).strip() if date_match else "2021-01-01"
        date_display = date_match.group(2).strip() if date_match else date_iso

        content_match = re.search(r'<div class="content">(.*?)</div>\s*</article>', raw_html, re.DOTALL)
        content = content_match.group(1).strip() if content_match else "<p>Content unavailable.</p>"
        content = clean_content_html(content, depth=2)

        meta = BLOG_META.get(slug, {
            "tag": "JOURNAL // ESSAY",
            "badge_class": "badge-emerald",
            "excerpt": "Gânduri și perspective.",
            "read_time": "5 MIN READ"
        })

        post_target_dir = output_dir / slug
        post_target_dir.mkdir(parents=True, exist_ok=True)

        page_html = f"""{get_html_head(f"{title} // Blog", depth=2)}
{get_header(active_nav="blog", depth=2)}

<main class="max-w-4xl mx-auto px-4 sm:px-6 py-10">
  <!-- BREADCRUMB / HUD -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="../../blog/" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-emerald-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO BLOG DIRECTORY</span>
    </a>
    <div class="flex items-center gap-2">
      <span class="{meta['badge_class']}">{meta['tag']}</span>
      <span class="status-pill">
        <span class="status-dot-emerald"></span>
        ARCHIVE DISPATCH
      </span>
    </div>
  </div>

  <!-- ARTICLE HEADER CARD -->
  <div class="tactical-card mb-8">
    <div class="flex flex-wrap items-center gap-3 font-mono text-xs text-slate-400 mb-3">
      <span class="inline-flex items-center gap-1 text-emerald-400 font-semibold">
        <i class="ph-bold ph-calendar-blank"></i>
        <time datetime="{date_iso}">{date_display}</time>
      </span>
      <span class="text-slate-700">•</span>
      <span class="inline-flex items-center gap-1 text-sky-400">
        <i class="ph-bold ph-clock"></i>
        {meta['read_time']}
      </span>
      <span class="text-slate-700">•</span>
      <span class="text-slate-400">DISPATCH #{slug.upper()}</span>
    </div>

    <h1 class="font-display font-bold text-2xl sm:text-4xl text-slate-100 leading-tight mb-4">
      {title}
    </h1>

    <div class="recessed-box text-xs font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
      <span>AUTHOR // DRAGOȘ IORGULESCU</span>
      <span>FORMAT // RAW DISPATCH ESSAY</span>
      <span>STATUS // PUBLISHED</span>
    </div>
  </div>

  <!-- ARTICLE BODY -->
  <article class="tactical-panel p-6 sm:p-10 prose-tactical">
    {content}
  </article>

  <!-- POST FOOTER ACTIONS -->
  <div class="mt-8 flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-[#111827]/60">
    <a href="../../blog/" class="tactical-btn">
      <i class="ph-bold ph-arrow-left"></i>
      BACK TO ALL DISPATCHES
    </a>
    <a href="#" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;" class="tactical-btn-emerald">
      <i class="ph-bold ph-arrow-up"></i>
      BACK TO TOP
    </a>
  </div>
</main>

{get_footer(depth=2)}"""

        with open(post_target_dir / "index.html", "w", encoding="utf-8") as pf:
            pf.write(page_html)

        posts_data.append({
            "slug": slug,
            "title": title,
            "date_iso": date_iso,
            "date_display": date_display,
            "meta": meta
        })

    # Sort posts by date descending
    posts_data.sort(key=lambda x: x["date_iso"], reverse=True)

    # Generate Blog Index
    blog_list_cards = ""
    for post in posts_data:
        m = post["meta"]
        blog_list_cards += f"""
        <article class="tactical-card glow-emerald group journal-entry">
          <div class="flex flex-wrap items-center justify-between gap-2 mb-3 font-mono text-xs">
            <div class="flex items-center gap-2">
              <span class="{m['badge_class']}">{m['tag']}</span>
              <span class="text-slate-500">•</span>
              <span class="text-emerald-400 font-semibold">{post['date_display']}</span>
            </div>
            <span class="text-slate-400 text-[11px]">{m['read_time']}</span>
          </div>

          <h2 class="font-display font-bold text-xl text-slate-100 group-hover:text-emerald-400 transition-colors mb-2">
            <a href="{post['slug']}/" class="hover:underline underline-offset-4">
              {post['title']}
            </a>
          </h2>

          <p class="text-sm text-slate-400 font-sans leading-relaxed mb-4">
            {m['excerpt']}
          </p>

          <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between font-mono text-xs">
            <a href="{post['slug']}/" class="inline-flex items-center gap-1.5 text-emerald-400 hover:text-emerald-300 font-semibold">
              READ COMPLETE DISPATCH
              <i class="ph-bold ph-arrow-right text-sm group-hover:translate-x-1 transition-transform"></i>
            </a>
            <span class="text-slate-400 uppercase text-[10px]">LOG // {post['slug'][:15]}</span>
          </div>
        </article>
        """

    blog_index_html = f"""{get_html_head("Journal // Blog", depth=1)}
{get_header(active_nav="blog", depth=1)}

<main class="max-w-7xl mx-auto px-4 sm:px-8 py-10">
  <!-- PAGE HEADER & STATUS -->
  <div class="tactical-panel p-6 sm:p-8 mb-10">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
      <div>
        <div class="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-emerald-400 mb-1">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          STREAM 01 // WRITTEN ESSAYS & NOTES
        </div>
        <h1 class="font-display font-bold text-3xl sm:text-4xl text-slate-100 tracking-tight">
          Journal & Thoughts
        </h1>
      </div>
      <div class="recessed-box font-mono text-xs text-slate-400 flex items-center gap-3">
        <span>TOTAL DISPATCHES: <strong class="text-emerald-400 font-bold">{len(posts_data)}</strong></span>
        <span class="text-slate-700">|</span>
        <span>INDEX // CHRONOLOGICAL</span>
      </div>
    </div>
    <p class="text-slate-400 text-sm max-w-3xl leading-relaxed">
      This is the place where some of my thoughts spill out onto the keyboard. Musings on digital addiction, software engineering craft, parental responsibility, cycling journeys, and physical training.
    </p>

    <!-- Client-side filter input -->
    <div class="mt-6 flex items-center gap-3">
      <div class="relative flex-1 max-w-md">
        <i class="ph-bold ph-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm"></i>
        <input 
          id="hud-filter-input"
          data-target=".journal-entry"
          type="text" 
          placeholder="FILTER DISPATCHES BY KEYWORD..." 
          class="w-full pl-9 pr-4 py-2 rounded-xl bg-[#0B0F17] border border-slate-800 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500/60 transition-colors"
        >
      </div>
      <span class="text-xs font-mono text-slate-400 hidden sm:inline">LIVE FILTER HUD</span>
    </div>
  </div>

  <!-- DISPATCHES GRID -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {blog_list_cards}
  </div>
</main>

{get_footer(depth=1)}"""

    with open(output_dir / "index.html", "w", encoding="utf-8") as bf:
        bf.write(blog_index_html)

    return posts_data

# Generate Howto Guides
def generate_howto_guides():
    howto_dir = BASE_DIR / "public" / "howto"
    output_dir = BASE_DIR / "howto"
    output_dir.mkdir(exist_ok=True)
    
    guides_data = []

    for guide_folder in sorted(howto_dir.glob("*/index.html")):
        slug = guide_folder.parent.name
        with open(guide_folder, "r", encoding="utf-8") as f:
            raw_html = f.read()

        title_match = re.search(r'<h1>(.*?)</h1>', raw_html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else slug.capitalize()

        content_match = re.search(r'<div class="content">(.*?)</div>\s*</article>', raw_html, re.DOTALL)
        content = content_match.group(1).strip() if content_match else "<p>Guide content unavailable.</p>"
        content = clean_content_html(content, depth=2)

        meta = HOWTO_META.get(slug, {
            "date": "2020-01-01",
            "tag": "SYSADMIN // TECH",
            "badge_class": "badge-sky",
            "excerpt": "Technical how-to documentation.",
            "read_time": "5 MIN READ"
        })

        guide_target_dir = output_dir / slug
        guide_target_dir.mkdir(parents=True, exist_ok=True)

        page_html = f"""{get_html_head(f"{title} // How-To", depth=2)}
{get_header(active_nav="howto", depth=2)}

<main class="max-w-4xl mx-auto px-4 sm:px-6 py-10">
  <!-- BREADCRUMB / HUD -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="../../howto/" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-sky-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO HOW-TO DIRECTORY</span>
    </a>
    <div class="flex items-center gap-2">
      <span class="{meta['badge_class']}">{meta['tag']}</span>
      <span class="status-pill">
        <span class="status-dot-sky"></span>
        TECHNICAL MANUAL
      </span>
    </div>
  </div>

  <!-- GUIDE HEADER CARD -->
  <div class="tactical-card mb-8">
    <div class="flex flex-wrap items-center gap-3 font-mono text-xs text-slate-400 mb-3">
      <span class="inline-flex items-center gap-1 text-sky-400 font-semibold">
        <i class="ph-bold ph-calendar-blank"></i>
        <span>{meta['date']}</span>
      </span>
      <span class="text-slate-700">•</span>
      <span class="inline-flex items-center gap-1 text-emerald-400">
        <i class="ph-bold ph-clock"></i>
        {meta['read_time']}
      </span>
      <span class="text-slate-700">•</span>
      <span class="text-slate-400">MANUAL // {slug.upper()}</span>
    </div>

    <h1 class="font-display font-bold text-2xl sm:text-4xl text-slate-100 leading-tight mb-4">
      {title}
    </h1>

    <div class="recessed-box text-xs font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
      <span>ENVIRONMENT // LINUX &bull; UNIX &bull; WINDOWS</span>
      <span>CLASSIFICATION // SYSTEM ADMINISTRATION</span>
      <span>STATUS // VERIFIED</span>
    </div>
  </div>

  <!-- GUIDE CONTENT -->
  <article class="tactical-panel p-6 sm:p-10 prose-tactical">
    {content}
  </article>

  <!-- POST FOOTER ACTIONS -->
  <div class="mt-8 flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-[#111827]/60">
    <a href="../../howto/" class="tactical-btn">
      <i class="ph-bold ph-arrow-left"></i>
      BACK TO HOW-TO INDEX
    </a>
    <a href="#" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;" class="tactical-btn-emerald">
      <i class="ph-bold ph-arrow-up"></i>
      BACK TO TOP
    </a>
  </div>
</main>

{get_footer(depth=2)}"""

        with open(guide_target_dir / "index.html", "w", encoding="utf-8") as gf:
            gf.write(page_html)

        guides_data.append({
            "slug": slug,
            "title": title,
            "date": meta["date"],
            "meta": meta
        })

    guides_data.sort(key=lambda x: x["date"], reverse=True)

    # Generate Howto Index
    howto_list_cards = ""
    for guide in guides_data:
        m = guide["meta"]
        howto_list_cards += f"""
        <article class="tactical-card glow-sky group howto-entry">
          <div class="flex flex-wrap items-center justify-between gap-2 mb-3 font-mono text-xs">
            <div class="flex items-center gap-2">
              <span class="{m['badge_class']}">{m['tag']}</span>
              <span class="text-slate-500">•</span>
              <span class="text-sky-400 font-semibold">{guide['date']}</span>
            </div>
            <span class="text-slate-400 text-[11px]">{m['read_time']}</span>
          </div>

          <h2 class="font-display font-bold text-xl text-slate-100 group-hover:text-sky-400 transition-colors mb-2">
            <a href="{guide['slug']}/" class="hover:underline underline-offset-4">
              {guide['title']}
            </a>
          </h2>

          <p class="text-sm text-slate-400 font-sans leading-relaxed mb-4">
            {m['excerpt']}
          </p>

          <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between font-mono text-xs">
            <a href="{guide['slug']}/" class="inline-flex items-center gap-1.5 text-sky-400 hover:text-sky-300 font-semibold">
              OPEN PROTOCOL MANUAL
              <i class="ph-bold ph-arrow-right text-sm group-hover:translate-x-1 transition-transform"></i>
            </a>
            <span class="text-slate-400 uppercase text-[10px]">DOC // {guide['slug'][:15]}</span>
          </div>
        </article>
        """

    howto_index_html = f"""{get_html_head("Technical How-To Manuals", depth=1)}
{get_header(active_nav="howto", depth=1)}

<main class="max-w-7xl mx-auto px-4 sm:px-8 py-10">
  <!-- PAGE HEADER & STATUS -->
  <div class="tactical-panel p-6 sm:p-8 mb-10">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
      <div>
        <div class="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-sky-400 mb-1">
          <span class="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse"></span>
          STREAM 04 // STEP-BY-STEP ENGINEERING PROTOCOLS
        </div>
        <h1 class="font-display font-bold text-3xl sm:text-4xl text-slate-100 tracking-tight">
          Technical How-Tos
        </h1>
      </div>
      <div class="recessed-box font-mono text-xs text-slate-400 flex items-center gap-3">
        <span>TOTAL GUIDES: <strong class="text-sky-400 font-bold">{len(guides_data)}</strong></span>
        <span class="text-slate-700">|</span>
        <span>DOMAIN // SYSADMIN & DEV</span>
      </div>
    </div>
    <p class="text-slate-400 text-sm max-w-3xl leading-relaxed">
      Step-by-step guides, configuration notes, and solutions derived from daily work with embedded testing, Linux clusters, virtualization, and minimal Unix toolchains.
    </p>

    <!-- Client-side filter input -->
    <div class="mt-6 flex items-center gap-3">
      <div class="relative flex-1 max-w-md">
        <i class="ph-bold ph-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm"></i>
        <input 
          id="hud-filter-input"
          data-target=".howto-entry"
          type="text" 
          placeholder="FILTER GUIDES (FREEBSD, POWERSHELL, HYPER-V, PI CLUSTER)..." 
          class="w-full pl-9 pr-4 py-2 rounded-xl bg-[#0B0F17] border border-slate-800 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500/60 transition-colors"
        >
      </div>
      <span class="text-xs font-mono text-slate-400 hidden sm:inline">LIVE FILTER HUD</span>
    </div>
  </div>

  <!-- GUIDES GRID -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {howto_list_cards}
  </div>
</main>

{get_footer(depth=1)}"""

    with open(output_dir / "index.html", "w", encoding="utf-8") as hf:
        hf.write(howto_index_html)

    return guides_data

# Generate Training Programs
def generate_training_programs():
    programe_dir = BASE_DIR / "programe"
    programe_dir.mkdir(exist_ok=True)

    # 1. Tension Spectrum
    ts_source = BASE_DIR / "public" / "programe" / "tension-spectrum" / "index.html"
    with open(ts_source, "r", encoding="utf-8") as f:
        ts_raw = f.read()
    ts_content_match = re.search(r'<div class="content">(.*?)</div>\s*</article>', ts_raw, re.DOTALL)
    ts_content = ts_content_match.group(1).strip() if ts_content_match else ""
    ts_content = clean_content_html(ts_content, depth=2)

    ts_content = re.sub(
        r'<a href=".*?tension-spectrum\.pdf".*?>(.*?)</a>',
        r'<a href="javascript:window.print()" class="tactical-btn-emerald"><i class="ph-bold ph-printer"></i> TIPĂREȘTE / DESCARCĂ PROTOCOLUL (PDF)</a>',
        ts_content
    )

    ts_target_dir = programe_dir / "tension-spectrum"
    ts_target_dir.mkdir(parents=True, exist_ok=True)

    ts_html = f"""{get_html_head("Tension Spectrum // Training Framework", depth=2)}
{get_header(active_nav="programe", depth=2)}

<main class="max-w-4xl mx-auto px-4 sm:px-6 py-10">
  <!-- BREADCRUMB / HUD -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="../../programe/" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-emerald-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO TRAINING DIRECTORY</span>
    </a>
    <div class="flex items-center gap-2">
      <span class="badge-emerald">STRONGFIRST GIRYA // PROTOCOL</span>
      <span class="status-pill">
        <span class="status-dot-emerald"></span>
        ACTIVE METHODOLOGY
      </span>
    </div>
  </div>

  <!-- HERO CARD -->
  <div class="tactical-card mb-8">
    <div class="flex flex-wrap items-center gap-3 font-mono text-xs text-slate-400 mb-3">
      <span class="text-emerald-400 font-semibold">FRAMEWORK // 01</span>
      <span class="text-slate-700">•</span>
      <span class="text-slate-400">FOCUS // FUNCTIONAL HYPERTROPHY & TENSION CONTROL</span>
      <span class="text-slate-700">•</span>
      <span class="text-amber-400">SYSTEM // STRONGFIRST PRINCIPLES</span>
    </div>

    <h1 class="font-display font-bold text-3xl sm:text-5xl text-slate-100 leading-tight mb-4">
      Tension Spectrum
    </h1>

    <div class="recessed-box text-xs font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
      <span>FREQUENCY // 5-DAY HYBRID SPLIT</span>
      <span>GOAL // HYPERTROPHY WITHOUT CNS EXHAUSTION</span>
      <span>RECOVERY // HIGH COMPLIANCE</span>
    </div>
  </div>

  <!-- ARTICLE BODY -->
  <article class="tactical-panel p-6 sm:p-10 prose-tactical">
    {ts_content}
  </article>

  <!-- POST FOOTER ACTIONS -->
  <div class="mt-8 flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-[#111827]/60">
    <a href="../../programe/" class="tactical-btn">
      <i class="ph-bold ph-arrow-left"></i>
      BACK TO TRAINING PROGRAMS
    </a>
    <button onclick="window.print()" class="tactical-btn-emerald">
      <i class="ph-bold ph-printer"></i>
      PRINT / EXPORT PROTOCOL
    </button>
  </div>
</main>

{get_footer(depth=2)}"""

    with open(ts_target_dir / "index.html", "w", encoding="utf-8") as tsf:
        tsf.write(ts_html)

    # 2. SFG I & SFB Prep
    sfg_source = BASE_DIR / "content" / "programe" / "sfg-prep.md"
    with open(sfg_source, "r", encoding="utf-8") as f:
        sfg_raw = f.read()

    # Extract all poster divs from sfg-prep.md
    posters = re.findall(r'<div class="poster">(.*?)</div>\s*(?=<div class="poster">|$)', sfg_raw, re.DOTALL)
    
    sfg_target_dir = programe_dir / "sfg-prep"
    sfg_target_dir.mkdir(parents=True, exist_ok=True)

    # Clean and style SFG posters into Tactical Dark
    sfg_posters_styled = ""
    for idx, p_content in enumerate(posters, 1):
        grid_m = re.search(r'(<div class="grid-container">.*)</div>\s*<div class="bottom-directive">', p_content, re.DOTALL)
        grid_html = (grid_m.group(1) + "</div>") if grid_m else ""
        focus_m = re.search(r'<div class="focus-box">(.*?)</div>', p_content, re.DOTALL)
        focus_html = focus_m.group(1) if focus_m else ""
        directive_m = re.search(r'<div class="bottom-directive">(.*?)</div>', p_content, re.DOTALL)
        directive_html = directive_m.group(1) if directive_m else ""
        title_m = re.search(r'<div class="phase-title-text">(.*?)</div>', p_content)
        phase_title = title_m.group(1) if title_m else f"Phase 0{idx}"

        sfg_posters_styled += f"""
        <section class="tactical-panel p-6 sm:p-8 mb-8 border border-slate-800">
          <div class="flex flex-wrap items-center justify-between gap-4 pb-4 mb-6 border-b border-slate-800">
            <div class="flex items-center gap-4">
              <span class="font-display font-extrabold text-4xl sm:text-5xl text-amber-500 font-mono">0{idx}</span>
              <div>
                <span class="font-mono text-xs uppercase tracking-widest text-slate-400">PHASE 0{idx} // SFG LEVEL 1 + SFB</span>
                <h2 class="font-display font-bold text-xl sm:text-2xl text-slate-100">
                  {phase_title}
                </h2>
              </div>
            </div>
            <div class="font-mono text-xs text-right">
              <span class="badge-amber">LIFT HEAVY. BE KIND.</span>
            </div>
          </div>

          <!-- Focus Guidance -->
          <div class="recessed-box mb-6 border-l-4 border-l-amber-500 text-sm text-slate-300">
            {focus_html}
          </div>

          <!-- Poster Content Grid -->
          <div class="prose-tactical text-sm">
            {grid_html}
          </div>

          <!-- Coach Directive -->
          <div class="mt-6 p-4 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs text-slate-400">
            {directive_html}
          </div>
        </section>
        """

    sfg_html = f"""{get_html_head("SFG I & SFB Prep // 3-Phase Blueprint", depth=2)}
{get_header(active_nav="programe", depth=2)}

<main class="max-w-5xl mx-auto px-4 sm:px-6 py-10">
  <!-- BREADCRUMB / HUD -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="../../programe/" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-amber-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO TRAINING DIRECTORY</span>
    </a>
    <div class="flex items-center gap-2">
      <span class="badge-amber">STRONGFIRST CERTIFICATION PROTOCOL</span>
      <span class="status-pill">
        <span class="status-dot-amber"></span>
        8-MONTH PROGRESSION
      </span>
    </div>
  </div>

  <!-- HERO CARD -->
  <div class="tactical-card mb-8">
    <div class="flex flex-wrap items-center gap-3 font-mono text-xs text-slate-400 mb-3">
      <span class="text-amber-400 font-semibold">FRAMEWORK // 02</span>
      <span class="text-slate-700">•</span>
      <span class="text-slate-400">TARGET // STRONGFIRST GIRYA 1 & BODYWEIGHT</span>
      <span class="text-slate-700">•</span>
      <span class="text-emerald-400">STRUCTURE // 3 PROGRESSIVE PHASES</span>
    </div>

    <h1 class="font-display font-bold text-3xl sm:text-5xl text-slate-100 leading-tight mb-4">
      Program de Pregătire SFG I & SFB
    </h1>

    <p class="text-slate-400 text-sm max-w-3xl leading-relaxed mb-4">
      Un program de antrenament progresiv, structurat în 3 faze mari pe 8 luni, pentru pregătirea certificărilor StrongFirst Girya (SFG) Nivelul 1 și StrongFirst Bodyweight (SFB). Îmbină Rite of Passage, anduranța alactică (A+A), și simularea celor 3 zile consecutive de stres de la certificare.
    </p>

    <div class="recessed-box text-xs font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
      <span>PHASE 1: FOUNDATION (ROP & S&S)</span>
      <span>PHASE 2: DOUBLE KB & A+A EMOM</span>
      <span>PHASE 3: CERTIFICATION SIMULATION</span>
    </div>
  </div>

  <!-- PHASES -->
  {sfg_posters_styled}

  <!-- FOOTER ACTIONS -->
  <div class="mt-8 flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-[#111827]/60">
    <a href="../../programe/" class="tactical-btn">
      <i class="ph-bold ph-arrow-left"></i>
      BACK TO TRAINING DIRECTORY
    </a>
    <button onclick="window.print()" class="tactical-btn-emerald">
      <i class="ph-bold ph-printer"></i>
      PRINT FULL PROGRAM
    </button>
  </div>
</main>

{get_footer(depth=2)}"""

    with open(sfg_target_dir / "index.html", "w", encoding="utf-8") as sfgf:
        sfgf.write(sfg_html)

    # 3. BJJ & Rehabilitation Prep
    bjj_target_dir = programe_dir / "bjj-prep"
    bjj_target_dir.mkdir(parents=True, exist_ok=True)

    bjj_html = f"""{get_html_head("Program Pregătire BJJ & Reabilitare", depth=2)}
{get_header(active_nav="programe", depth=2)}

<main class="max-w-5xl mx-auto px-4 sm:px-6 py-10">
  <!-- BREADCRUMB / HUD -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="../../programe/" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-purple-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO TRAINING DIRECTORY</span>
    </a>
    <div class="flex items-center gap-2">
      <span class="badge-purple">BJJ PREP & REHABILITATION</span>
      <span class="status-pill">
        <span class="status-dot-sky"></span>
        ACTIVE RECOVERY HUD
      </span>
    </div>
  </div>

  <!-- HERO CARD -->
  <div class="tactical-card mb-8">
    <div class="flex flex-wrap items-center gap-3 font-mono text-xs text-slate-400 mb-3">
      <span class="text-purple-400 font-semibold">FRAMEWORK // 03</span>
      <span class="text-slate-700">•</span>
      <span class="text-slate-400">FOCUS // ELBOW REHAB (TENDINITIS) & ZONE 2 BASE</span>
      <span class="text-slate-700">•</span>
      <span class="text-sky-400">DISCIPLINE // BRAZILIAN JIU-JITSU & KETTLEBELL</span>
    </div>

    <h1 class="font-display font-bold text-3xl sm:text-5xl text-slate-100 leading-tight mb-4">
      Program Pregătire BJJ & Reabilitare
    </h1>

    <p class="text-slate-400 text-sm max-w-3xl leading-relaxed mb-4">
      Protocol special structurat pentru vindecarea tendinitei de cot, construirea unei baze aerobe solide în Zona 2 (bicicletă staționară, rucking sau alergare lentă), mobilitate specifică pentru sol (BJJ) și forță structurală prin kettlebells.
    </p>

    <div class="recessed-box text-xs font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
      <span>PERIOD // IULIE – SEPTEMBRIE</span>
      <span>MICRO-ROUTINE // DAILY 5–7 MIN ELBOW REHAB</span>
      <span>CARDIO // ZONE 2 CONSTANT (NO CORTISOL SPIKES)</span>
    </div>
  </div>

  <!-- DAILY MICRO ROUTINE -->
  <div class="tactical-card mb-8 border-purple-500/30">
    <div class="flex items-center gap-2 font-mono text-xs text-purple-400 font-semibold uppercase tracking-wider mb-3">
      <i class="ph-bold ph-wrench text-base"></i>
      Micro-Rutina Zilnică: Cot & Antebraț (5–7 minute)
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
      <div class="recessed-box border-slate-800">
        <strong class="text-slate-200 block mb-1">1. Izometrie încheietură (90°):</strong>
        <span class="text-slate-400">3 serii &times; 30–45 sec. menținere</span>
      </div>
      <div class="recessed-box border-slate-800">
        <strong class="text-slate-200 block mb-1">2. Coborâri excentrice lente:</strong>
        <span class="text-slate-400">3 serii &times; 10–12 rep. (coborâre 4–5 sec.)</span>
      </div>
      <div class="recessed-box border-slate-800">
        <strong class="text-slate-200 block mb-1">3. Extensii degete cu elastic:</strong>
        <span class="text-slate-400">2–3 serii &times; 15–20 rep.</span>
      </div>
    </div>
  </div>

  <!-- WEEKLY SCHEDULE TABLE -->
  <div class="tactical-panel p-6 sm:p-8 mb-8 overflow-x-auto">
    <div class="font-display font-bold text-xl text-slate-100 mb-4 flex items-center justify-between">
      <span>Plan Săptămânal de Lucru</span>
      <span class="font-mono text-xs text-slate-400">7-DAY PROTOCOL</span>
    </div>

    <table class="w-full text-left font-sans text-xs sm:text-sm border-collapse">
      <thead>
        <tr class="border-b border-slate-800 font-mono text-xs text-slate-400 uppercase bg-[#0B0F17]">
          <th class="p-3 w-24">Ziua</th>
          <th class="p-3 w-40">Focus Principal</th>
          <th class="p-3">Blocul 1: Forță / Core / Mobilitate</th>
          <th class="p-3 w-64">Blocul 2: Bază Aerobă (Zona 2)</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/60 font-sans text-xs sm:text-sm">
        <tr class="hover:bg-slate-900/30">
          <td class="p-3 font-mono font-bold text-emerald-400">LUNI</td>
          <td class="p-3 font-semibold text-slate-300">KB & Bază Aerobă</td>
          <td class="p-3">
            <ul class="list-disc list-inside space-y-1 text-slate-300">
              <li><strong>Goblet Squat (16 kg):</strong> 3 x 5 (pauză 3s jos)</li>
              <li><strong>Double KB Deadlift (2x20 kg):</strong> 4 x 8 (Dead-stop)</li>
              <li><strong>Turkish Get-Up (12–14 kg):</strong> 3 / parte</li>
            </ul>
          </td>
          <td class="p-3 font-mono text-sky-400">
            <span class="block text-slate-200 font-semibold">30 min (Zona 2 constant)</span>
            <span class="text-slate-400 text-xs font-sans">Opțiuni: Bicicletă staționară, rucking sau alergare lentă Zona 2</span>
          </td>
        </tr>
        <tr class="hover:bg-slate-900/30">
          <td class="p-3 font-mono font-bold text-purple-400">MARȚI</td>
          <td class="p-3 font-semibold text-slate-300">Mobilitate BJJ & Core</td>
          <td class="p-3">
            <ul class="list-disc list-inside space-y-1 text-slate-300">
              <li><strong>Bridge & Reach:</strong> 2 x 8 / parte | <strong>Shrimpings:</strong> 3 x 10 / parte</li>
              <li><strong>Flotări Hardstyle/RKC:</strong> 3–4 x 3–5 rep pe pumni</li>
              <li><strong>Tuck Hollow Hold:</strong> 4 x 15–20 sec. (spatele lipit)</li>
            </ul>
          </td>
          <td class="p-3 font-mono text-purple-400">Mobilitate pasivă: Couch Stretch & 90/90 (60s/parte)</td>
        </tr>
        <tr class="hover:bg-slate-900/30">
          <td class="p-3 font-mono font-bold text-sky-400">MIERCURI</td>
          <td class="p-3 font-semibold text-slate-300">Cardio & Reîncărcare</td>
          <td class="p-3 text-slate-400 italic">Pauză completă pentru brațe și picioare.</td>
          <td class="p-3 font-mono text-sky-400">
            <span class="block text-slate-200 font-semibold">35–40 min (Ritm lejer)</span>
            <span class="text-slate-400 text-xs font-sans">Opțiuni: Bicicletă staționară, rucking sau alergare lentă Zona 2</span>
          </td>
        </tr>
        <tr class="hover:bg-slate-900/30">
          <td class="p-3 font-mono font-bold text-emerald-400">JOI</td>
          <td class="p-3 font-semibold text-slate-300">KB & Structură Upper</td>
          <td class="p-3">
            <ul class="list-disc list-inside space-y-1 text-slate-300">
              <li><strong>Goblet Squat (16 kg):</strong> 3 x 5 | <strong>Single KB Deadlift (32 kg):</strong> 4 x 6–8</li>
              <li><strong>Turkish Get-Up (12–14 kg):</strong> 3–4 / parte</li>
              <li><strong>Flotări Hardstyle:</strong> 3–4 x 3–5 rep.</li>
              <li><strong>Ramat izometric la inele/chingi:</strong> 3 x 20–30 sec.</li>
            </ul>
          </td>
          <td class="p-3 font-mono text-slate-400">
            <span class="block text-slate-300">Opțional: 15–20 min refacere</span>
            <span class="text-slate-400 text-xs font-sans">Pedalat lejer, rucking sau alergare ușoară Zona 2</span>
          </td>
        </tr>
        <tr class="hover:bg-slate-900/30">
          <td class="p-3 font-mono font-bold text-purple-400">VINERI</td>
          <td class="p-3 font-semibold text-slate-300">Mobilitate & Core BJJ</td>
          <td class="p-3">
            <ul class="list-disc list-inside space-y-1 text-slate-300">
              <li><strong>Bridge & Reach + Shrimpings:</strong> Rulaj 15 min</li>
              <li><strong>Tuck Hollow Hold:</strong> 4 x 15–20 sec.</li>
              <li><strong>Întinderi coloană toracică:</strong> 5 min</li>
            </ul>
          </td>
          <td class="p-3 font-mono text-sky-400">
            <span class="block text-slate-200 font-semibold">20–30 min (Rulaj foarte lejer)</span>
            <span class="text-slate-400 text-xs font-sans">Opțiuni: Bicicletă staționară, rucking sau alergare lentă Zona 2</span>
          </td>
        </tr>
        <tr class="hover:bg-slate-900/30">
          <td class="p-3 font-mono font-bold text-amber-400">SÂMBĂTĂ</td>
          <td class="p-3 font-semibold text-slate-300">Soare & Parc</td>
          <td class="p-3">
            <ul class="list-disc list-inside space-y-1 text-slate-300">
              <li><strong>Mers alert pe bucla din parc (1.6 km)</strong></li>
              <li><strong>Scări:</strong> 3–5 urcări cadențate (călcat cu toată talpa, împins din călcâi/fesieri)</li>
            </ul>
          </td>
          <td class="p-3 font-mono text-amber-400">
            <span class="block text-amber-300 font-semibold">Aerob în aer liber: 45–60 min</span>
            <span class="text-slate-400 text-xs font-sans">Rucking (cu vestă/rucsac), mers alert sau alergare lentă Zona 2</span>
          </td>
        </tr>
        <tr class="hover:bg-slate-900/30">
          <td class="p-3 font-mono font-bold text-slate-400">DUMINICĂ</td>
          <td class="p-3 font-semibold text-slate-300">Odihnă Activă</td>
          <td class="p-3 text-slate-400 italic">Plimbare lejeră cu familia. Fără cronometru sau structură.</td>
          <td class="p-3 font-mono text-emerald-400 font-semibold">Refacere completă & Somn</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- GOLDEN RULES -->
  <div class="tactical-panel p-6 sm:p-8 border-amber-500/30 bg-amber-500/5 mb-8">
    <div class="font-mono text-xs uppercase tracking-wider text-amber-400 font-bold mb-4 flex items-center gap-2">
      <i class="ph-bold ph-shield-check text-base"></i>
      Reguli de Aur pentru Menținerea Sănătății Structurale
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono text-xs">
      <div class="recessed-box">
        <strong class="text-amber-300 block mb-1">FLOTĂRI HARDSTYLE:</strong>
        <p class="text-slate-300">Tensiune 100%, corp rigid ca o scândură, expir presurizat (Power Breath). Calitate maximă pe 3–5 repetări.</p>
      </div>
      <div class="recessed-box">
        <strong class="text-amber-300 block mb-1">HOLLOW HOLD:</strong>
        <p class="text-slate-300">Dacă zona lombară se desprinde 1 mm de sol, oprește seria imediat. Respiră scurt „sub scut”.</p>
      </div>
      <div class="recessed-box">
        <strong class="text-amber-300 block mb-1">MONITORIZARE COT:</strong>
        <p class="text-slate-300">Dacă simți rigiditate crescută a doua zi dimineață, scade volumul la kettlebell cu 20% și crește excentricele.</p>
      </div>
    </div>
  </div>

  <!-- ACTIONS -->
  <div class="mt-8 flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-[#111827]/60">
    <a href="../../programe/" class="tactical-btn">
      <i class="ph-bold ph-arrow-left"></i>
      BACK TO TRAINING DIRECTORY
    </a>
    <button onclick="window.print()" class="tactical-btn-emerald">
      <i class="ph-bold ph-printer"></i>
      PRINT BJJ PROTOCOL
    </button>
  </div>
</main>

{get_footer(depth=2)}"""

    with open(bjj_target_dir / "index.html", "w", encoding="utf-8") as bjjf:
        bjjf.write(bjj_html)

    # 4. Training Programs Index
    programe_index_html = f"""{get_html_head("Training Frameworks // Overview", depth=1)}
{get_header(active_nav="programe", depth=1)}

<main class="max-w-7xl mx-auto px-4 sm:px-8 py-10">
  <!-- PAGE HEADER & STATUS -->
  <div class="tactical-panel p-6 sm:p-8 mb-10">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
      <div>
        <div class="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-emerald-400 mb-1">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          STREAM 02 // GENERAL PHYSICAL PREPARATION & CONDITIONING
        </div>
        <h1 class="font-display font-bold text-3xl sm:text-4xl text-slate-100 tracking-tight">
          Training Frameworks
        </h1>
      </div>
      <div class="recessed-box font-mono text-xs text-slate-400 flex items-center gap-3">
        <span>ACTIVE SYSTEMS: <strong class="text-emerald-400 font-bold">03</strong></span>
        <span class="text-slate-700">|</span>
        <span>PHILOSOPHY // STRONGFIRST HARDSTYLE</span>
      </div>
    </div>
    <p class="text-slate-400 text-sm max-w-3xl leading-relaxed">
      A structured collection of training programs, protocols, and conditioning blueprints conceived or adapted over years of kettlebell lifting, bodyweight mastery, and tendon rehabilitation. Shared freely for serious practitioners.
    </p>
  </div>

  <!-- FRAMEWORKS BENTO GRID -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
    <!-- Card 1: Tension Spectrum -->
    <div class="tactical-card glow-emerald flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between gap-2 mb-4">
          <span class="badge-emerald">HYPERTROPHY & TENSION</span>
          <span class="text-xs font-mono text-slate-400">01 // PROTOCOL</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4">
          <i class="ph-duotone ph-barbell text-2xl"></i>
        </div>
        <h2 class="font-display font-bold text-2xl text-slate-100 mb-2">
          <a href="tension-spectrum/" class="hover:text-emerald-400 transition-colors">Tension Spectrum</a>
        </h2>
        <p class="text-sm text-slate-400 font-sans leading-relaxed mb-6">
          Un framework avansat de antrenament axat pe manipularea tensiunii musculare, complexe specifice cu kettlebell (Complex 1: Structural Mobility, Complex 2: 10-8-5-3-2-1), loaded stretching și supracompensare fără uzură neurală.
        </p>
      </div>
      <div class="pt-4 border-t border-slate-800">
        <a href="tension-spectrum/" class="tactical-btn-emerald w-full">
          VIEW TENSION SPECTRUM
          <i class="ph-bold ph-arrow-right"></i>
        </a>
      </div>
    </div>

    <!-- Card 2: SFG 1 & SFB Prep -->
    <div class="tactical-card glow-amber flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between gap-2 mb-4">
          <span class="badge-amber">CERTIFICATION // 8 MONTHS</span>
          <span class="text-xs font-mono text-slate-400">02 // PROTOCOL</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4">
          <i class="ph-duotone ph-shield-check text-2xl"></i>
        </div>
        <h2 class="font-display font-bold text-2xl text-slate-100 mb-2">
          <a href="sfg-prep/" class="hover:text-amber-400 transition-colors">SFG I & SFB Prep</a>
        </h2>
        <p class="text-sm text-slate-400 font-sans leading-relaxed mb-6">
          Blueprint în 3 faze progressive pentru promovarea certificărilor StrongFirst Girya Nivelul 1 și StrongFirst Bodyweight. Include Rite of Passage, anduranță alactică A+A EMOM, Snatch Test și simulare de weekend pe duble.
        </p>
      </div>
      <div class="pt-4 border-t border-slate-800">
        <a href="sfg-prep/" class="tactical-btn w-full hover:border-amber-500/50 hover:text-amber-400">
          VIEW SFG BLUEPRINT
          <i class="ph-bold ph-arrow-right"></i>
        </a>
      </div>
    </div>

    <!-- Card 3: BJJ & Rehab -->
    <div class="tactical-card glow-purple flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between gap-2 mb-4">
          <span class="badge-purple">REHABILITATION & JIU-JITSU</span>
          <span class="text-xs font-mono text-slate-400">03 // PROTOCOL</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4">
          <i class="ph-duotone ph-heartbeat text-2xl"></i>
        </div>
        <h2 class="font-display font-bold text-2xl text-slate-100 mb-2">
          <a href="bjj-prep/" class="hover:text-purple-400 transition-colors">BJJ & Reabilitare</a>
        </h2>
        <p class="text-sm text-slate-400 font-sans leading-relaxed mb-6">
          Protocol de recuperare a cotului (epicondilită/tendinită) combinat cu rezistență aerobă mitocondrială (Zona 2 prin bicicletă staționară, rucking sau alergare lentă), mobilitate sol (Shrimpings, Bridge & Reach) și forță izometrică.
        </p>
      </div>
      <div class="pt-4 border-t border-slate-800">
        <a href="bjj-prep/" class="tactical-btn w-full hover:border-purple-500/50 hover:text-purple-400">
          VIEW BJJ PROTOCOL
          <i class="ph-bold ph-arrow-right"></i>
        </a>
      </div>
    </div>
  </div>

  <!-- SUPPLEMENTAL HUD BOX -->
  <div class="tactical-panel p-6 sm:p-8">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
      <div class="md:col-span-8">
        <span class="badge-sky mb-2">CARDIOVASCULAR CONDITIONING</span>
        <h3 class="font-display font-bold text-2xl text-slate-100 mb-2">
          Navy Seal Burpees & Zona 2
        </h3>
        <p class="text-sm text-slate-400 max-w-2xl leading-relaxed">
          Protocoale cu greutatea corpului executate în ritm controlat pentru anduranță cardiovasculară pură, fără acidificare excesivă. Ideal pentru menținerea inimii și a metabolismului lipidic.
        </p>
      </div>
      <div class="md:col-span-4 flex justify-start md:justify-end">
        <a href="../kettlebell/" class="tactical-btn">
          READ PROTOCOL
          <i class="ph-bold ph-arrow-right"></i>
        </a>
      </div>
    </div>
  </div>
</main>

{get_footer(depth=1)}"""

    with open(programe_dir / "index.html", "w", encoding="utf-8") as pf:
        pf.write(programe_index_html)

# Generate Kettlebell Page
def generate_kettlebell_page():
    target_dir = BASE_DIR / "kettlebell"
    target_dir.mkdir(exist_ok=True)

    kb_html = f"""{get_html_head("Kettlebell & Conditioning // Protocol", depth=1)}
{get_header(depth=1)}

<main class="max-w-4xl mx-auto px-4 sm:px-6 py-10">
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="../" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-emerald-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO HOME HUD</span>
    </a>
    <span class="badge-emerald">HARDSTYLE CONDITIONING</span>
  </div>

  <div class="tactical-card mb-8">
    <div class="flex items-center gap-2 font-mono text-xs text-emerald-400 mb-2">
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
      PHYSICAL READINESS PROTOCOL
    </div>
    <h1 class="font-display font-bold text-3xl sm:text-4xl text-slate-100 mb-4">
      Kettlebell & Conditioning
    </h1>
    <p class="text-slate-400 text-sm max-w-2xl leading-relaxed">
      Principiile de bază ale forței funcționale: tensiune maximă pe mișcările de presă și genuflexiuni, explozie pură alactică pe mișcările de balans și relaxare instantanee Fast & Loose între seturi.
    </p>
  </div>

  <article class="tactical-panel p-6 sm:p-10 prose-tactical">
    <h2>1. Navy Seal Burpees: Protocol de Anduranță Aerobă</h2>
    <p>
      Navy Seal Burpees (varianta cu 2 flotări rigide și 3 genunchi aduși la piept per repetiție) reprezintă unul dintre cele mai eficiente teste de anduranță musculară fără impact articular agresiv. 
    </p>
    <ul>
      <li><strong>Format recomandat:</strong> 10 serii a câte 5 repetiții (50 rep totale), cu pauză ghidată strict de respirația nazală.</li>
      <li><strong>Regulă tehnică:</strong> Fiecare flotare se execută pe pumni sau pe palme cu trunchiul complet rigid (Hollow Body). Fără arcuiri lombare.</li>
      <li><strong>Obiectiv fiziologic:</strong> Stimularea oxidării acizilor grași și anduranță mitocondrială.</li>
    </ul>

    <h2>2. Hardstyle Kettlebell Basics</h2>
    <p>
      Baza oricărui progres structural rămâne stăpânirea mișcărilor fundamentale din școala StrongFirst:
    </p>
    <ul>
      <li><strong>The Swing (Balansul cu 1 și 2 mâini):</strong> Explozie din bazin, proiecție balistică a greutății și lockout complet în picioare.</li>
      <li><strong>The Turkish Get-Up (TGU):</strong> Stabilitate scapulară, mobilitate de șold și control corporal în toate cele 3 planuri de mișcare.</li>
      <li><strong>The Clean & Press:</strong> Forță strictă a umerilor și trunchiului, ancorată pe stabilitate gluteală.</li>
    </ul>

    <h2>3. Programe Specializate</h2>
    <p>
      Pentru protocoale complete de antrenament și cicluri pe săptămâni, consultă secțiunea dedicată de <a href="../programe/">Programe de Antrenament</a> (Tension Spectrum, SFG 1 Prep și BJJ Prep).
    </p>
  </article>
</main>

{get_footer(depth=1)}"""

    with open(target_dir / "index.html", "w", encoding="utf-8") as kbf:
        kbf.write(kb_html)

# Generate Sounds Page
def generate_sounds_page():
    target_dir = BASE_DIR / "sounds"
    target_dir.mkdir(exist_ok=True)

    sounds_html = f"""{get_html_head("Sounds // Audio Archive", depth=1)}
{get_header(active_nav="sounds", depth=1)}

<main class="max-w-5xl mx-auto px-4 sm:px-6 py-10">
  <!-- BREADCRUMB / HUD -->
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="../" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-purple-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO HOME HUD</span>
    </a>
    <div class="flex items-center gap-2">
      <span class="badge-purple">AUDIO ARCHIVES // SYNTHESIZERS</span>
      <span class="status-pill">
        <span class="status-dot-sky"></span>
        STREAM 03
      </span>
    </div>
  </div>

  <!-- HERO CARD -->
  <div class="tactical-card mb-8">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
      <div class="md:col-span-7">
        <div class="flex items-center gap-2 font-mono text-xs text-purple-400 mb-2">
          <span class="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
          AUDIO ARCHIVE // 2008 – PRESENT
        </div>
        <h1 class="font-display font-bold text-3xl sm:text-5xl text-slate-100 mb-4">
          Sounds & Audio
        </h1>
        <p class="text-slate-400 text-sm leading-relaxed mb-4">
          Ever since I was a child, I loved sounds. Over the years, I've explored computers, drums, bass guitars, and modular / hardware synthesizers in order to chase soundscapes, drone metal, ambient textures, and experimental electronica. Self-taught, minimal, and unfiltered.
        </p>
        <div class="recessed-box font-mono text-xs text-slate-400 flex flex-wrap items-center gap-3">
          <span>MONIKERS: <strong>5 PROJECTS</strong></span>
          <span>•</span>
          <span>MEDIA: <strong>YOUTUBE &bull; BANDCAMP &bull; ARCHIVE.ORG</strong></span>
        </div>
      </div>
      <div class="md:col-span-5">
        <img src="../images/sounds.png" alt="Synthesizer setup" class="w-full rounded-2xl border border-slate-800 shadow-2xl">
      </div>
    </div>
  </div>

  <!-- PROJECTS BENTO GRID -->
  <div class="space-y-6">
    <!-- Project 1: Scentient Pencils -->
    <div class="tactical-panel p-6 sm:p-8 border-purple-500/30">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
        <span class="badge-purple">2020 – PRESENT // ACTIVE MONIKER</span>
        <span class="font-mono text-xs text-slate-400">MODULAR &bull; AMBIENT &bull; FIELD RECORDINGS</span>
      </div>
      <h2 class="font-display font-bold text-2xl text-slate-100 mb-2">
        Scentient Pencils
      </h2>
      <p class="text-sm text-slate-300 font-sans leading-relaxed mb-4">
        The name under which I sometimes put out various recordings or live sessions. Born at the beginning of 2020, while experimenting with ambient sounds in my living room. Mainly revolving around hardware synths, some acoustics, sound textures, ambient soundscapes, and field recordings.
      </p>
      <div class="flex flex-wrap gap-3">
        <a href="https://www.youtube.com/channel/UCMUYR9Kyk4JZxifm84lW7Bg" target="_blank" class="tactical-btn-emerald">
          <i class="ph-bold ph-youtube-logo text-base"></i>
          YOUTUBE CHANNEL
        </a>
        <a href="https://scentientpencils.bandcamp.com" target="_blank" class="tactical-btn">
          <i class="ph-bold ph-music-note text-base"></i>
          BANDCAMP PAGE
        </a>
      </div>
    </div>

    <!-- Project 2: Sentem -->
    <div class="tactical-panel p-6 sm:p-8">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
        <span class="badge-amber">2011 – 2016 // ARCHIVED</span>
        <span class="font-mono text-xs text-slate-400">DRONE ROCK &bull; DRONE METAL &bull; DARK AMBIENT</span>
      </div>
      <h2 class="font-display font-bold text-2xl text-slate-100 mb-2">
        Sentem
      </h2>
      <p class="text-sm text-slate-300 font-sans leading-relaxed mb-4">
        My former solo project active between 2011 and 2016. Drone rock, drone metal, dark ambient, and experimental guitar textures. Probably my favorite release is the “Alean” EP (November 2014), blending dark ambient, droney guitars, and subtle folk elements.
      </p>
      <div>
        <a href="https://sentem.bandcamp.com" target="_blank" class="tactical-btn">
          <i class="ph-bold ph-music-note text-base"></i>
          SENTEM ON BANDCAMP
        </a>
      </div>
    </div>

    <!-- Project 3: Versta -->
    <div class="tactical-panel p-6 sm:p-8">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
        <span class="badge-sky">EXPERIMENTAL ELECTRONICA</span>
        <span class="font-mono text-xs text-slate-400">LIVE SESSION RECORDING</span>
      </div>
      <h2 class="font-display font-bold text-2xl text-slate-100 mb-2">
        Versta
      </h2>
      <p class="text-sm text-slate-300 font-sans leading-relaxed mb-4">
        A short-lived moniker. The most notable recording is a live experimental electronica session titled <em>Versta Septentrionalica</em>.
      </p>
      <div>
        <a href="https://soundcloud.com/deep-roller-rec/versta-septentrionalica" target="_blank" class="tactical-btn">
          <i class="ph-bold ph-play text-base"></i>
          LISTEN ON SOUNDCLOUD
        </a>
      </div>
    </div>

    <!-- Project 4: Soul Overload -->
    <div class="tactical-panel p-6 sm:p-8">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
        <span class="badge-slate">2008 – 2010 // EARLY WORK</span>
        <span class="font-mono text-xs text-slate-400">ARCHIVE.ORG SURVIVAL</span>
      </div>
      <h2 class="font-display font-bold text-2xl text-slate-100 mb-2">
        Soul Overload
      </h2>
      <p class="text-sm text-slate-300 font-sans leading-relaxed mb-4">
        Quite a cheesy teenage name, but it was what it was. My very first attempts at solo recordings. Three surviving tracks are preserved on the Internet Archive.
      </p>
      <div>
        <a href="https://archive.org/details/souloverload-dystopia" target="_blank" class="tactical-btn">
          <i class="ph-bold ph-archive text-base"></i>
          ARCHIVE.ORG DYSTOPIA
        </a>
      </div>
    </div>

    <!-- Project 5: Tulbur -->
    <div class="tactical-panel p-6 sm:p-8">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
        <span class="badge-slate">2009 // BAND ARCHIVE</span>
        <span class="font-mono text-xs text-slate-400">GRUNGE &bull; ALTERNATIVE METAL &bull; DRUMS</span>
      </div>
      <h2 class="font-display font-bold text-2xl text-slate-100 mb-2">
        Tulbur
      </h2>
      <p class="text-sm text-slate-300 font-sans leading-relaxed mb-4">
        A project started with two good friends and colleagues in 2009. Grunge and Tool-like influences. Played bass and drums.
      </p>
      <div class="flex flex-wrap gap-3">
        <a href="https://soundcloud.com/ciprian-lazar/green-yellow-brown" target="_blank" class="tactical-btn">
          <i class="ph-bold ph-play text-base"></i>
          GREEN, YELLOW, BROWN (DRUMS)
        </a>
        <a href="https://soundcloud.com/ciprian-lazar/dosp" target="_blank" class="tactical-btn">
          <i class="ph-bold ph-play text-base"></i>
          DOSP
        </a>
      </div>
    </div>
  </div>
</main>

{get_footer(depth=1)}"""

    with open(target_dir / "index.html", "w", encoding="utf-8") as sf:
        sf.write(sounds_html)

# Generate Now Page
def generate_now_page():
    now_html = f"""{get_html_head("Now // Current Focus", depth=0)}
{get_header(active_nav="now", depth=0)}

<main class="max-w-4xl mx-auto px-4 sm:px-6 py-10">
  <div class="mb-8 flex flex-wrap items-center justify-between gap-3 font-mono text-xs text-slate-400">
    <a href="./" class="inline-flex items-center gap-1.5 text-slate-400 hover:text-emerald-400 transition-colors">
      <i class="ph-bold ph-arrow-left"></i>
      <span>// RETURN TO HOME HUD</span>
    </a>
    <span class="badge-emerald">CURRENT FOCUS &bull; WHAT I'M UP TO</span>
  </div>

  <div class="tactical-card mb-8 glow-emerald">
    <div class="flex items-center gap-2 font-mono text-xs text-emerald-400 mb-2">
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
      REAL-TIME FOCUS // BUCHAREST, RO
    </div>
    <h1 class="font-display font-bold text-3xl sm:text-5xl text-slate-100 mb-4">
      What I'm Doing "Now"
    </h1>
    <p class="text-slate-400 text-sm max-w-2xl leading-relaxed">
      Inspired by Derek Sivers' <a href="https://nownownow.com/about" target="_blank" class="text-emerald-400 underline">/now page</a> movement. A public declaration of current priorities, engineering goals, physical training, and life balance.
    </p>
  </div>

  <div class="space-y-6">
    <div class="tactical-panel p-6 sm:p-8">
      <div class="flex items-center gap-2 font-mono text-xs text-emerald-400 uppercase tracking-wider mb-3">
        <i class="ph-bold ph-briefcase text-base"></i>
        01 // Engineering & Craft
      </div>
      <h2 class="font-display font-bold text-xl text-slate-100 mb-2">
        Software Test Engineering & Embedded Device Automation
      </h2>
      <p class="text-slate-300 text-sm leading-relaxed mb-3">
        Deeply involved in building and maintaining test automation frameworks for embedded devices and prototype hardware (specifically DAMF - Device Automation & Management Framework). Focusing on high reliability, reproducible runs, and eliminating flaky tests.
      </p>
      <div class="recessed-box font-mono text-xs text-slate-400">
        ENVIRONMENT // Python, Linux daemons, serial communications, suckless toolchains, QEMU/virtualization.
      </div>
    </div>

    <div class="tactical-panel p-6 sm:p-8">
      <div class="flex items-center gap-2 font-mono text-xs text-amber-400 uppercase tracking-wider mb-3">
        <i class="ph-bold ph-barbell text-base"></i>
        02 // Physical Conditioning
      </div>
      <h2 class="font-display font-bold text-xl text-slate-100 mb-2">
        StrongFirst Girya & Tension Manipulation
      </h2>
      <p class="text-slate-300 text-sm leading-relaxed mb-3">
        Refining the <em>Tension Spectrum</em> methodology: daily loaded stretching, kettlebell ladders, tactical pull-ups, and Zone 2 aerobic maintenance. Rehabilitating elbow tendons through daily micro-routines while maintaining strong overhead pressing mechanics.
      </p>
      <div class="recessed-box font-mono text-xs text-slate-400">
        FOCUS // Rite of Passage, Heavy Doubles EMOM, Navy Seal Burpees, Fast & Loose recovery.
      </div>
    </div>

    <div class="tactical-panel p-6 sm:p-8">
      <div class="flex items-center gap-2 font-mono text-xs text-purple-400 uppercase tracking-wider mb-3">
        <i class="ph-bold ph-waveform text-base"></i>
        03 // Audio Explorations
      </div>
      <h2 class="font-display font-bold text-xl text-slate-100 mb-2">
        Scentient Pencils & Analog Synthesis
      </h2>
      <p class="text-slate-300 text-sm leading-relaxed mb-3">
        Toying with hardware synthesizers, ambient texture generators, and field recordings. Recording unpolished living-room sessions that prioritize raw mood over studio perfection.
      </p>
    </div>

    <div class="tactical-panel p-6 sm:p-8">
      <div class="flex items-center gap-2 font-mono text-xs text-sky-400 uppercase tracking-wider mb-3">
        <i class="ph-bold ph-house-line text-base"></i>
        04 // Family & Digital Minimalism
      </div>
      <h2 class="font-display font-bold text-xl text-slate-100 mb-2">
        Being Present & Conscious
      </h2>
      <p class="text-slate-300 text-sm leading-relaxed">
        Father of two energetic boys. Constantly fighting the dopamine traps of smartphones and social media. Practicing intentional disconnection, outdoor park walks, bicycle tours, and reading physical books.
      </p>
    </div>
  </div>
</main>

{get_footer(depth=0)}"""

    with open(BASE_DIR / "now.html", "w", encoding="utf-8") as nf:
        nf.write(now_html)

# Generate Home Page
def generate_home_page(posts, guides):
    # Top 3 latest blog posts
    recent_posts_html = ""
    for p in posts[:3]:
        m = p["meta"]
        recent_posts_html += f"""
        <div class="p-4 rounded-xl bg-[#0B0F17] border border-slate-800 hover:border-slate-700 transition-all group">
          <div class="flex items-center justify-between text-xs font-mono mb-1.5">
            <span class="{m['badge_class']} text-[10px] py-0.5">{m['tag'].split('//')[0].strip()}</span>
            <span class="text-slate-500">{p['date_display']}</span>
          </div>
          <h3 class="font-display font-bold text-base text-slate-100 group-hover:text-emerald-400 transition-colors">
            <a href="blog/{p['slug']}/">{p['title']}</a>
          </h3>
          <p class="text-xs text-slate-400 font-sans mt-1 line-clamp-2">
            {m['excerpt']}
          </p>
        </div>
        """

    # Top 3 latest guides
    recent_guides_html = ""
    for g in guides[:3]:
        m = g["meta"]
        recent_guides_html += f"""
        <div class="p-4 rounded-xl bg-[#0B0F17] border border-slate-800 hover:border-slate-700 transition-all group">
          <div class="flex items-center justify-between text-xs font-mono mb-1.5">
            <span class="{m['badge_class']} text-[10px] py-0.5">{m['tag'].split('//')[0].strip()}</span>
            <span class="text-slate-500">{g['date']}</span>
          </div>
          <h3 class="font-display font-bold text-base text-slate-100 group-hover:text-sky-400 transition-colors">
            <a href="howto/{g['slug']}/">{g['title']}</a>
          </h3>
          <p class="text-xs text-slate-400 font-sans mt-1 line-clamp-2">
            {m['excerpt']}
          </p>
        </div>
        """

    home_html = f"""{get_html_head("Dragoș Iorgulescu // Tactical Dark HUD", depth=0)}
{get_header(depth=0)}

<main class="max-w-7xl mx-auto px-4 sm:px-8 py-8 sm:py-12">
  <!-- BENTO GRID SYSTEM -->
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
            <span class="text-2xl font-bold text-slate-100 font-mono block">08</span>
            <span class="text-[10px] uppercase text-emerald-400 tracking-wider">DISPATCHES</span>
          </div>
          <div class="recessed-box">
            <span class="text-2xl font-bold text-slate-100 font-mono block">07</span>
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
        <!-- Program 1: Tension Spectrum -->
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

        <!-- Program 2: SFG 1 & SFB Prep -->
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

        <!-- Program 3: BJJ Prep -->
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
        <!-- Project 1 -->
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

        <!-- Project 2 -->
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

        <!-- General Interests -->
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

    with open(BASE_DIR / "index.html", "w", encoding="utf-8") as hf:
        hf.write(home_html)

def main():
    print("Generating pure HTML site with Tactical Dark / Bento HUD style...")
    posts = generate_blog_posts()
    print(f"Generated {len(posts)} blog posts + blog index.")
    guides = generate_howto_guides()
    print(f"Generated {len(guides)} howto guides + howto index.")
    generate_training_programs()
    print("Generated training programs.")
    generate_kettlebell_page()
    print("Generated kettlebell page.")
    generate_sounds_page()
    print("Generated sounds page.")
    generate_now_page()
    print("Generated now page.")
    generate_home_page(posts, guides)
    print("Generated home page.")
    print("Build complete! All HTML files created successfully.")

if __name__ == "__main__":
    main()
