#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TACTICAL DARK // JINJA2-BASED SITE BUILDER
Dragoș Iorgulescu - Clean, Maintainable Static Site Generator

This is the new Jinja2-based builder that replaces publish.py.
It provides the same functionality but with clean template separation.

Usage:
  python3 build.py --rebuild
  python3 build.py --serve 8080
"""

import sys
import os
import re
import html
import math
import shutil
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Initialize Jinja2
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "public"
TEMPLATES_DIR = BASE_DIR / "templates"
CONTENT_DIR = BASE_DIR / "content"

# Initialize Jinja2 environment
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True
)

# =============================================================================
# SITE GLOBAL CONFIGURATION
# =============================================================================
SITE_CONFIG = {
    "author": "Dragoș Iorgulescu",
    "handle": "Dragoș Iorgulescu",
    "subtitle": "Test Engineer · Strength Practitioner",
    "subtitle_short": "Test Engineer &middot; Strength Practitioner &middot; Bucharest, RO",
    "description": "Personal website, training frameworks, technical how-tos, and audio archives by Dragoș Iorgulescu.",
    "tagline": "Lift heavy. Be kind. Build robust software.",
    "location": "Bucharest, RO",
    "site_title_suffix": "Dragoș Iorgulescu",
    "site_url": "https://iorgos.net",
    "email": "dragos@iorgos.net",
    "mastodon": "https://mastodon.social/@diorgulescu",
    "github": "https://github.com/diorgulescu",
    "youtube": "https://www.youtube.com/@iorgosnet",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_display_date(iso_date):
    """Format ISO date to display format (e.g., '02 Mar 2022')."""
    MONTHS = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
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
    """Convert text to URL slug."""
    text = text.lower()
    replacements = {
        'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ş': 's', 'ț': 't', 'ţ': 't',
        'é': 'e', 'è': 'e', 'ó': 'o', 'ö': 'o', 'ü': 'u', 'ä': 'a'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^a-z0-9\-]+', '-', text)
    return text.strip('-')


def get_root_path(depth=0):
    """Get relative root path based on depth."""
    return "./" if depth == 0 else "../" * depth


# =============================================================================
# MARKDOWN PARSER (same as in publish.py)
# =============================================================================

def inline_format(text):
    """Format inline markdown elements."""
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
    """Parse markdown to HTML with frontmatter support."""
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

    # 1. Extract code blocks
    code_blocks = []
    def save_code(m):
        lang = m.group(1).strip()
        code = m.group(2)
        idx = len(code_blocks)
        cls = f' class="language-{lang}"' if lang else ''
        code_blocks.append(f'<pre><code{cls}>{html.escape(code.strip())}</code></pre>')
        return f'\n\n@@@CODE_BLOCK_{idx}@@@\n\n'

    body = re.sub(r'```(\w*)\n(.*?)```', save_code, body, flags=re.DOTALL)

    # 2. Extract raw HTML blocks
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

        # Markdown Table
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


# =============================================================================
# VALIDATION
# =============================================================================

def validate_frontmatter(meta, category, filepath=""):
    """Validate frontmatter metadata for consistency and completeness."""
    errors = []
    warnings = []
    
    # Validate title
    if not meta.get("title"):
        if filepath:
            errors.append(f"[ERR // VALIDATION] Missing 'title' in {filepath}")
        else:
            errors.append("[ERR // VALIDATION] Missing 'title' in frontmatter")
    
    # Validate date format
    date_str = meta.get("date")
    if date_str:
        try:
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d %b %Y"]:
                try:
                    datetime.strptime(str(date_str).strip().split()[0], fmt)
                    break
                except ValueError:
                    continue
            else:
                if filepath:
                    warnings.append(f"[WARN // VALIDATION] Invalid date format '{date_str}' in {filepath}")
                else:
                    warnings.append(f"[WARN // VALIDATION] Invalid date format '{date_str}'")
        except Exception:
            if filepath:
                warnings.append(f"[WARN // VALIDATION] Could not parse date '{date_str}' in {filepath}")
            else:
                warnings.append(f"[WARN // VALIDATION] Could not parse date '{date_str}'")
    else:
        if category == "blog":
            if filepath:
                warnings.append(f"[WARN // VALIDATION] Missing 'date' in {filepath}")
            else:
                warnings.append("[WARN // VALIDATION] Missing 'date' in frontmatter")
    
    # Validate slug
    slug = meta.get("slug")
    if slug:
        if not re.match(r'^[a-z0-9-]+$', slug):
            if filepath:
                warnings.append(f"[WARN // VALIDATION] Slug '{slug}' in {filepath} contains invalid characters")
            else:
                warnings.append(f"[WARN // VALIDATION] Slug '{slug}' contains invalid characters")
    
    # Validate category
    if category and category not in ["blog", "howto", "programe"]:
        if filepath:
            warnings.append(f"[WARN // VALIDATION] Unknown category '{category}' in {filepath}")
        else:
            warnings.append(f"[WARN // VALIDATION] Unknown category '{category}'")
    
    # Validate tag
    tag = meta.get("tag")
    if tag and len(tag) > 50:
        if filepath:
            warnings.append(f"[WARN // VALIDATION] Tag too long in {filepath}")
        else:
            warnings.append("[WARN // VALIDATION] Tag too long")
    
    # Validate excerpt
    excerpt = meta.get("excerpt")
    if excerpt and len(excerpt) > 300:
        if filepath:
            warnings.append(f"[WARN // VALIDATION] Excerpt too long in {filepath}")
        else:
            warnings.append("[WARN // VALIDATION] Excerpt too long")
    
    return len(errors) == 0, errors, warnings


# =============================================================================
# TEMPLATE RENDERING HELPERS
# =============================================================================

def render_page(template_name, **context):
    """Render a Jinja2 template with context."""
    context.update({
        'site_author': SITE_CONFIG['author'],
        'site_handle': SITE_CONFIG['handle'],
        'site_subtitle': SITE_CONFIG['subtitle'],
        'site_subtitle_short': SITE_CONFIG['subtitle_short'],
        'site_description': SITE_CONFIG['description'],
        'site_tagline': SITE_CONFIG['tagline'],
        'site_location': SITE_CONFIG['location'],
        'site_url': SITE_CONFIG['site_url'],
        'site_email': SITE_CONFIG['email'],
        'site_mastodon': SITE_CONFIG['mastodon'],
        'site_github': SITE_CONFIG['github'],
        'site_youtube': SITE_CONFIG['youtube'],
        'current_year': datetime.now().year,
    })
    
    template = jinja_env.get_template(template_name)
    return template.render(**context)


def clean_content_paths(content_html, depth=0):
    """Adjust image and link paths to be relative."""
    root_path = get_root_path(depth)
    cleaned = re.sub(r'src=["\']/images/(.*?)["\']', f'src="{root_path}images/\\1"', content_html)
    cleaned = re.sub(r'href=["\']/images/(.*?)["\']', f'href="{root_path}images/\\1"', cleaned)
    cleaned = re.sub(r'href=["\']/docs/(.*?)["\']', f'href="{root_path}docs/\\1"', cleaned)
    return cleaned


# =============================================================================
# PAGE GENERATORS
# =============================================================================

def generate_single_article(meta, content_html, category, slug):
    """Generate a single article page."""
    target_dir = OUTPUT_DIR / category / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    title = meta.get("title", slug.capitalize())
    date_iso = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
    date_display = format_display_date(date_iso)
    read_time = meta.get("read_time", "5 MIN READ")

    content_clean = clean_content_paths(content_html, depth=2)

    category_labels = {
        "blog": "Journal",
        "howto": "How-To",
        "programe": "Programs"
    }
    category_label = category_labels.get(category, category.capitalize())
    page_title = f"{title} // {category_label}"
    
    page_html = render_page(
        f"{category}/post.html",
        page_title=page_title,
        title=title,
        date_iso=date_iso,
        date_display=date_display,
        read_time=read_time,
        content=content_clean,
        category_label=category_label,
        root_path=get_root_path(2)
    )

    with open(target_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(page_html)


def generate_category_index(category, items):
    """Generate category index page."""
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

    entries = []
    for item in items:
        entries.append({
            'slug': item['slug'],
            'title': item.get('title', item['slug'].capitalize()),
            'date': item.get('date', '2021-01-01'),
            'date_display': item.get('date_display', item.get('date', '2021-01-01')),
            'excerpt': item.get('excerpt', ''),
            'read_time': item.get('read_time', '5 MIN READ')
        })

    category_title = category_titles.get(category, category.capitalize())
    page_title = category_title

    page_html = render_page(
        f"{category}/index.html",
        page_title=page_title,
        category_title=category_title,
        category_description=category_descriptions.get(category, ""),
        entries=entries,
        root_path=get_root_path(1),
        active_nav=category
    )

    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(page_html)


def generate_program_index(programs, category_meta):
    """Generate programe category index page with custom layout."""
    output_dir = OUTPUT_DIR / "programe"
    output_dir.mkdir(parents=True, exist_ok=True)

    programs_list = []
    for prog in programs:
        programs_list.append({
            'slug': prog['slug'],
            'title': prog.get('title', prog['slug'].capitalize()),
            'description': prog.get('description', prog.get('excerpt', '')),
            'badge': prog.get('badge', f"{prog.get('badge_number', '00')} // {prog.get('badge_text', 'PHYSICAL PREPARATION')}")
        })

    # Get category metadata from _index.md if available
    category_title = category_meta.get('title', 'Training Frameworks')
    description = category_meta.get('content', 'Structured physical preparation frameworks, kettlebell progressions, and conditioning protocols.')

    page_html = render_page(
        "programe/index.html",
        page_title=category_title,
        description=description,
        programs=programs_list,
        content=category_meta.get('content_html', ''),
        root_path=get_root_path(1),
        active_nav="programe"
    )

    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(page_html)


def generate_standalone_page(template_name, output_path, meta, content_html):
    """Generate a standalone page from a template."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    title = meta.get('title', output_path.stem.replace('-', ' ').capitalize())
    date_display = format_display_date(meta.get('date', ''))
    
    page_html = render_page(
        template_name,
        page_title=title,
        title=title,
        date_display=date_display,
        tag=meta.get('tag', ''),
        content=content_html,
        root_path=get_root_path(0)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(page_html)


def generate_home_page(posts, guides, programe=None):
    """Generate the homepage."""
    if programe is None:
        programe = []
    
    # Top 5 latest blog posts
    recent_posts = []
    for item in posts[:5]:
        recent_posts.append({
            'slug': item['slug'],
            'title': item.get('title', item['slug'].capitalize()),
            'date': item.get('date', ''),
            'date_display': item.get('date_display', ''),
            'read_time': item.get('read_time', '5 MIN READ')
        })

    # Top 5 latest guides
    recent_guides = []
    for item in guides[:5]:
        recent_guides.append({
            'slug': item['slug'],
            'title': item.get('title', item['slug'].capitalize()),
            'date': item.get('date', ''),
            'date_display': item.get('date_display', ''),
            'read_time': item.get('read_time', '5 MIN READ')
        })

    # Programs for home page (use all or first 3)
    programs = []
    for item in programe[:3]:
        programs.append({
            'slug': item['slug'],
            'title': item.get('title', item['slug'].capitalize()),
            'description': item.get('description', item.get('excerpt', '')),
            'badge': item.get('badge', f"{item.get('badge_number', len(programs) + 1):02d} // {item.get('badge_text', 'PHYSICAL PREPARATION')}")
        })

    page_html = render_page(
        "index.html",
        page_title=SITE_CONFIG['author'],
        recent_posts=recent_posts,
        recent_guides=recent_guides,
        programs=programs,
        blog_count=len(posts),
        howto_count=len(guides),
        programe_count=len(programe),
        root_path=get_root_path(0),
        active_nav=''
    )

    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(page_html)


def generate_now_page():
    """Generate the now page from content/now.md."""
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

    page_html = render_page(
        "now.html",
        page_title=f"{title} // Now",
        title=title,
        content=content_clean,
        updated=updated,
        location=location,
        tag=tag,
        root_path=get_root_path(0),
        active_nav='now'
    )

    with open(OUTPUT_DIR / "now.html", "w", encoding="utf-8") as fp:
        fp.write(page_html)
    
    print("[SYS // NOW] Generated public/now.html from content/now.md")
    return True


def generate_search_page():
    """Generate the search page."""
    page_html = render_page(
        "search.html",
        page_title="Search",
        root_path=get_root_path(0),
        active_nav=''
    )
    
    with open(OUTPUT_DIR / "search.html", "w", encoding="utf-8") as fp:
        fp.write(page_html)
    print("[SYS // SEARCH] Generated public/search.html")


def generate_search_index(blog_items, howto_items):
    """Generate search index JSON for lunr.js."""
    import json
    
    index_data = []
    
    # Add blog posts
    for item in blog_items:
        index_data.append({
            "id": f"blog/{item['slug']}/",
            "title": item.get("title", item["slug"]),
            "url": f"/blog/{item['slug']}/",
            "excerpt": item.get("excerpt", ""),
            "content": item.get("content_html", ""),
            "category": "blog",
            "category_name": "Journal",
            "date": item.get("date", ""),
            "tag": item.get("tag", ""),
            "read_time": item.get("read_time", "")
        })
    
    # Add how-to guides
    for item in howto_items:
        index_data.append({
            "id": f"howto/{item['slug']}/",
            "title": item.get("title", item["slug"]),
            "url": f"/howto/{item['slug']}/",
            "excerpt": item.get("excerpt", ""),
            "content": item.get("content_html", ""),
            "category": "howto",
            "category_name": "How-To",
            "date": item.get("date", ""),
            "tag": item.get("tag", ""),
            "read_time": item.get("read_time", "")
        })
    
    # Strip HTML tags from content for better search
    html_tag_pattern = re.compile(r'<[^>]+>')
    for doc in index_data:
        doc['content_clean'] = html_tag_pattern.sub(' ', doc.get('content', '')).strip()
        doc['content_clean'] = ' '.join(doc['content_clean'].split())
    
    # Sort by date descending
    index_data.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # Write index file
    index_file = OUTPUT_DIR / "js" / "search-index.json"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(index_file, "w", encoding="utf-8") as fp:
        json.dump(index_data, fp, ensure_ascii=False, indent=2)
    
    print(f"[SYS // SEARCH] Generated public/js/search-index.json with {len(index_data)} entries")


def generate_rss_feed(blog_items):
    """Generate RSS 2.0 feed for blog section."""
    if not blog_items:
        print("[WARN // RSS] No blog items found, skipping RSS feed generation")
        return

    base_url = SITE_CONFIG.get("site_url", "https://iorgos.net").rstrip("/")
    site_title = SITE_CONFIG.get("author", "Dragoș Iorgulescu")
    site_description = "Personal website, training frameworks, technical how-tos, and audio archives by Dragoș Iorgulescu."
    now = datetime.now(timezone.utc)
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Sort blog items by date descending
    sorted_items = sorted(blog_items, key=lambda x: str(x["date"]), reverse=True)

    author_name = SITE_CONFIG.get("author", "Dragoș Iorgulescu")
    author_email = SITE_CONFIG.get("email", "dragos@iorgos.net")

    # Format dates for RSS
    for item in sorted_items:
        date_str = item.get("date", "2021-01-01")
        try:
            dt = datetime.strptime(str(date_str).strip().split()[0], "%Y-%m-%d")
            item["pub_date_formatted"] = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        except (ValueError, TypeError):
            item["pub_date_formatted"] = pub_date

    template = jinja_env.get_template("rss.xml")
    page_html = template.render(
        site_title=site_title,
        site_description=site_description,
        base_url=base_url,
        pub_date=pub_date,
        author_name=author_name,
        author_email=author_email,
        items=sorted_items
    )

    # Write to both locations
    for feed_path in ["feed.xml", "blog/feed.xml"]:
        feed_file = OUTPUT_DIR / feed_path
        feed_file.parent.mkdir(parents=True, exist_ok=True)
        with open(feed_file, "w", encoding="utf-8") as fp:
            fp.write(page_html)
    
    print(f"[SYS // RSS] Generated public/feed.xml with {len(sorted_items)} blog entries")


def generate_sitemap(blog_items, howto_items, programe_items=None):
    """Generate sitemap.xml and robots.txt."""
    if programe_items is None:
        programe_items = []
    
    base_url = SITE_CONFIG.get("site_url", "https://iorgos.net").rstrip("/")
    today_str = datetime.now().strftime("%Y-%m-%d")

    latest_blog_date = blog_items[0]["date"] if blog_items else today_str
    latest_howto_date = howto_items[0]["date"] if howto_items else today_str
    latest_programe_date = programe_items[0]["date"] if programe_items else today_str

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

    urls = [
        ("/", today_str, "weekly", "1.0"),
        ("/now.html", now_date, "weekly", "0.9"),
        ("/programe/", today_str, "weekly", "0.9"),
        ("/kettlebell/", kettlebell_date, "monthly", "0.8"),
        ("/sounds/", today_str, "monthly", "0.8"),
        ("/blog/", str(latest_blog_date)[:10], "weekly", "0.8"),
        ("/howto/", str(latest_howto_date)[:10], "weekly", "0.8"),
    ]

    for item in blog_items:
        date_val = str(item.get("date", today_str)).strip().strip('"').strip("'")[:10]
        urls.append((f"/blog/{item['slug']}/", date_val, "monthly", "0.7"))

    for item in howto_items:
        date_val = str(item.get("date", today_str)).strip().strip('"').strip("'")[:10]
        urls.append((f"/howto/{item['slug']}/", date_val, "monthly", "0.7"))
    
    for item in programe_items:
        date_val = str(item.get("date", today_str)).strip().strip('"').strip("'")[:10]
        urls.append((f"/programe/{item['slug']}/", date_val, "monthly", "0.7"))

    template = jinja_env.get_template("sitemap.xml")
    sitemap_content = template.render(
        base_url=base_url,
        urls=urls,
        today_str=today_str
    )

    with open(OUTPUT_DIR / "sitemap.xml", "w", encoding="utf-8") as fp:
        fp.write(sitemap_content)
    print(f"[SYS // SITEMAP] Generated public/sitemap.xml with {len(urls)} URLs")

    robots_content = f"""# robots.txt for {base_url}
User-agent: *
Allow: /

Sitemap: {base_url}/sitemap.xml
"""
    with open(OUTPUT_DIR / "robots.txt", "w", encoding="utf-8") as fp:
        fp.write(robots_content)
    print("[SYS // ROBOTS] Generated public/robots.txt")


def copy_static_assets():
    """Copy static assets to public/ directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    asset_folders = ["css", "js", "images"]
    for folder in asset_folders:
        src = BASE_DIR / folder
        dst = OUTPUT_DIR / folder
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)

    for filename in ["favicon.ico", "CNAME"]:
        extra_src = BASE_DIR / filename
        if extra_src.is_file():
            shutil.copy2(extra_src, OUTPUT_DIR / filename)


def load_and_compile_all():
    """Main function to load content and compile the entire site."""
    if not CONTENT_DIR.exists():
        print(f"[ERR // CONTENT] content/ directory not found at {CONTENT_DIR}")
        return [], []

    # 1. Copy static assets
    copy_static_assets()

    blog_items = []
    howto_items = []

    # 2. Process Blog
    blog_dir = CONTENT_DIR / "blog"
    if blog_dir.exists():
        for md_file in sorted(blog_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            with open(md_file, "r", encoding="utf-8") as fp:
                raw = fp.read()
            meta, content_html, body = parse_markdown(raw)

            # Validate frontmatter
            is_valid, errors, warnings = validate_frontmatter(meta, "blog", str(md_file))
            for error in errors:
                print(error)
            for warning in warnings:
                print(warning)
            if not is_valid:
                print(f"[ERR // VALIDATION] Skipping {md_file} due to validation errors")
                continue

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

    # Cleanup orphaned blog directories
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
    howto_dir = CONTENT_DIR / "howto"
    if howto_dir.exists():
        for md_file in sorted(howto_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            with open(md_file, "r", encoding="utf-8") as fp:
                raw = fp.read()
            meta, content_html, body = parse_markdown(raw)

            # Validate frontmatter
            is_valid, errors, warnings = validate_frontmatter(meta, "howto", str(md_file))
            for error in errors:
                print(error)
            for warning in warnings:
                print(warning)
            if not is_valid:
                print(f"[ERR // VALIDATION] Skipping {md_file} due to validation errors")
                continue

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

    # Cleanup orphaned howto directories
    active_howto_slugs = {item["slug"] for item in howto_items}
    howto_root = OUTPUT_DIR / "howto"
    if howto_root.exists():
        for sub in howto_root.iterdir():
            if sub.is_dir() and sub.name not in active_howto_slugs and not sub.name.startswith(("_", ".")):
                shutil.rmtree(sub)
                print(f"[SYS // CLEANUP] Removed orphaned guide directory: public/howto/{sub.name}/")

    howto_items.sort(key=lambda x: str(x["date"]), reverse=True)
    generate_category_index("howto", howto_items)

    # 3. Process Programe
    programe_items = []
    programe_dir = CONTENT_DIR / "programe"
    category_meta = {}
    
    if programe_dir.exists():
        # Load category metadata from _index.md
        index_md = programe_dir / "_index.md"
        if index_md.exists():
            with open(index_md, "r", encoding="utf-8") as fp:
                raw = fp.read()
            meta, content_html, body = parse_markdown(raw)
            category_meta = {
                'title': meta.get('title', 'Training Frameworks'),
                'content': body.strip(),
                'content_html': content_html
            }
        
        for md_file in sorted(programe_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            with open(md_file, "r", encoding="utf-8") as fp:
                raw = fp.read()
            meta, content_html, body = parse_markdown(raw)

            # Validate frontmatter
            is_valid, errors, warnings = validate_frontmatter(meta, "programe", str(md_file))
            for error in errors:
                print(error)
            for warning in warnings:
                print(warning)
            if not is_valid:
                print(f"[ERR // VALIDATION] Skipping {md_file} due to validation errors")
                continue

            slug = meta.get("slug") or md_file.stem

            is_draft = str(meta.get("draft", "false")).lower() in ["true", "1", "yes"]
            if is_draft:
                draft_dir = OUTPUT_DIR / "programe" / slug
                if draft_dir.is_dir():
                    shutil.rmtree(draft_dir)
                    print(f"[SYS // DRAFT] Removed unlisted HTML directory for draft: public/programe/{slug}/")
                continue

            title = meta.get("title") or slug.replace("-", " ").capitalize()
            date_iso = meta.get("date", "2020-01-01")
            date_display = format_display_date(date_iso)

            content_clean = clean_content_paths(content_html, depth=2)

            category_labels = {
                "blog": "Journal",
                "howto": "How-To",
                "programe": "Programs"
            }
            category_label = category_labels.get("programe", "Programs")
            page_title = f"{title} // {category_label}"
            
            page_html = render_page(
                "programe/post.html",
                page_title=page_title,
                title=title,
                date_iso=date_iso,
                date_display=date_display,
                content=content_clean,
                category_label=category_label,
                description=meta.get("description", ""),
                badge=meta.get("badge", f"{meta.get('badge_number', '00')} // {meta.get('badge_text', 'PHYSICAL PREPARATION')}"),
                root_path=get_root_path(2)
            )

            target_dir = OUTPUT_DIR / "programe" / slug
            target_dir.mkdir(parents=True, exist_ok=True)
            with open(target_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(page_html)

            item = {
                "slug": slug,
                "title": title,
                "date": date_iso,
                "date_display": date_display,
                "excerpt": meta.get("excerpt", meta.get("description", "")),
                "description": meta.get("description", ""),
                "badge": meta.get("badge", f"{meta.get('badge_number', len(programe_items) + 1):02d} // PHYSICAL PREPARATION"),
                "badge_number": meta.get("badge_number", len(programe_items) + 1),
                "badge_text": meta.get("badge_text", "PHYSICAL PREPARATION"),
                "content_html": content_html
            }

            programe_items.append(item)

        # Generate programe index
        generate_program_index(programe_items, category_meta)

    # Cleanup orphaned programe directories
    active_programe_slugs = {item["slug"] for item in programe_items}
    programe_root = OUTPUT_DIR / "programe"
    if programe_root.exists():
        for sub in programe_root.iterdir():
            if sub.is_dir() and sub.name not in active_programe_slugs and not sub.name.startswith(("_", ".")):
                shutil.rmtree(sub)
                print(f"[SYS // CLEANUP] Removed orphaned program directory: public/programe/{sub.name}/")

    programe_items.sort(key=lambda x: str(x["date"]), reverse=True)

    # 4. Process Standalone Pages (kettlebell.md, sounds.md)
    # Kettlebell page
    kettlebell_md = CONTENT_DIR / "kettlebell.md"
    if kettlebell_md.exists():
        with open(kettlebell_md, "r", encoding="utf-8") as fp:
            raw = fp.read()
        meta, content_html, body = parse_markdown(raw)
        generate_standalone_page("kettlebell.html", OUTPUT_DIR / "kettlebell" / "index.html", meta, content_html)
        print("[SYS // KETTLEBELL] Generated public/kettlebell/index.html")

    # Sounds page
    sounds_md = CONTENT_DIR / "sounds.md"
    if sounds_md.exists():
        with open(sounds_md, "r", encoding="utf-8") as fp:
            raw = fp.read()
        meta, content_html, body = parse_markdown(raw)
        generate_standalone_page("sounds.html", OUTPUT_DIR / "sounds" / "index.html", meta, content_html)
        print("[SYS // SOUNDS] Generated public/sounds/index.html")

    # 5. Generate home page
    generate_home_page(blog_items, howto_items, programe_items)

    # 5. Generate now page
    generate_now_page()

    # 6. Generate search page
    generate_search_page()

    # 7. Generate search index
    generate_search_index(blog_items, howto_items)

    # 8. Generate RSS feed
    generate_rss_feed(blog_items)

    # 9. Generate sitemap
    generate_sitemap(blog_items, howto_items, programe_items)

    return blog_items, howto_items, programe_items


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def serve_site(port=8080):
    """Start local HTTP server."""
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


def scaffold_draft(title, category="blog", tag=None):
    """Create a new draft markdown template."""
    slug = slugify(title)
    dest_dir = CONTENT_DIR / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    target_file = dest_dir / f"{slug}.md"

    if target_file.exists():
        print(f"[WARN // EXISTS] File already exists: {target_file.relative_to(BASE_DIR)}")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    default_tag = tag or ("TECH // GUIDE" if category == "howto" else "JOURNAL // ESSAY")
    badge_cls = "badge-sky" if category == "howto" else "badge-emerald"

    template = f"""---.type: frontmatter
.title: "{title}"
.date: {today}
.category: {category}
.slug: {slug}
.tag: "{default_tag}"
.badge_class: {badge_cls}
.excerpt: "Scurt rezumat al acestui articol pentru cardul din grila Bento."
.read_time: "5 MIN READ"
.draft: false
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
    print(f"To compile after editing: python3 build.py")


def delete_article(slug_or_path, forced_category=None):
    """Delete an article from content/ and its generated HTML folder, then rebuild the site."""
    p = Path(slug_or_path)
    slug = p.stem
    if slug == "index" and p.parent.name:
        slug = p.parent.name

    categories = [forced_category] if forced_category else ["blog", "howto", "programe"]
    deleted_md = False
    deleted_html = False

    for cat in categories:
        md_file = CONTENT_DIR / cat / f"{slug}.md"
        if md_file.is_file():
            md_file.unlink()
            print(f"[SYS // DELETE] Removed source markdown: content/{cat}/{slug}.md")
            deleted_md = True

        html_dir = OUTPUT_DIR / cat / slug
        if html_dir.is_dir():
            shutil.rmtree(html_dir)
            print(f"[SYS // CLEANUP] Removed HTML directory: public/{cat}/{slug}/")
            deleted_html = True

    if not deleted_md and not deleted_html:
        print(f"[WARN // NOT FOUND] No article or directory found matching '{slug_or_path}'.")
        return False

    print(f"\n[SYS // REBUILD] Rebuilding site indexes and HUD...")
    blog_items, howto_items, programe_items = load_and_compile_all()
    print(f"[SYS // STATUS] COMPLETE // Site synchronized without '{slug}'.")
    return True


def publish_markdown_file(filepath, forced_category=None):
    """Publish a single markdown file by copying to content/ and rebuilding."""
    p = Path(filepath)
    if not p.is_file():
        print(f"[ERR // FILE] File does not exist: {filepath}")
        sys.exit(1)

    # Special handling for now.md
    if p.name == "now.md":
        target = CONTENT_DIR / "now.md"
        if p.resolve() != target.resolve():
            shutil.copy2(p, target)
        load_and_compile_all()
        print(f"[SYS // PUBLISH] Successfully updated now.html from {p.name}")
        return

    with open(p, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Parse to get metadata
    meta, content_html, body = parse_markdown(raw_content)
    
    # Determine category
    category = forced_category or meta.get("category", "").lower().strip()
    if not category:
        parent_name = p.parent.name.lower()
        if parent_name in ["blog", "howto", "programe"]:
            category = parent_name
        else:
            category = "blog"
    
    if category not in ["blog", "howto", "programe"]:
        print(f"[WARN // CATEGORY] Unrecognized category '{category}', defaulting to 'blog'")
        category = "blog"

    # Validate frontmatter
    is_valid, errors, warnings = validate_frontmatter(meta, category, str(p))
    for error in errors:
        print(error)
    for warning in warnings:
        print(warning)
    
    if not is_valid:
        print(f"[ERR // VALIDATION] Frontmatter validation failed for {p}. Fix errors above.")
        sys.exit(1)

    # Title & slug
    title = meta.get("title")
    if not title:
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
    dest_content_dir = CONTENT_DIR / category
    dest_content_dir.mkdir(parents=True, exist_ok=True)
    dest_md_path = dest_content_dir / f"{slug}.md"

    # Copy/update content source
    shutil.copy2(p, dest_md_path)
    print(f"[SYS // INGEST] Source file saved to: {dest_md_path.relative_to(BASE_DIR)}")

    # Rebuild site
    print(f"[SYS // REBUILD] Rebuilding site...")
    load_and_compile_all()
    
    print(f"[SYS // PUBLISHED] Compiled public/{category}/{slug}/index.html")


def main():
    parser = argparse.ArgumentParser(
        description="Tactical Dark // Jinja2 Site Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 build.py articol-nou.md
  python3 build.py articol-nou.md --category howto
  python3 build.py --rebuild
  python3 build.py --delete compensare
  python3 build.py --new "Cum am configurat FreeBSD" --category howto
  python3 build.py --serve 8080
        """
    )
    parser.add_argument("file", nargs="?", help="Path to markdown file to ingest and publish")
    parser.add_argument("--category", "-c", choices=["blog", "howto", "programe"], help="Force specific category")
    parser.add_argument("--rebuild", "-r", action="store_true", help="Rebuild entire site")
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

    if args.rebuild:
        print("[SYS // REBUILD] Rebuilding entire site from content/ directory...")
        blog_items, howto_items, programe_items = load_and_compile_all()
        print(f"[SYS // STATUS] COMPLETE // {len(blog_items)} blog posts, {len(howto_items)} howto guides & {len(programe_items)} programs compiled.")
        return

    # Default: rebuild all
    print("[SYS // REBUILD] Rebuilding entire site from content/ directory...")
    blog_items, howto_items, programe_items = load_and_compile_all()
    print(f"[SYS // STATUS] COMPLETE // {len(blog_items)} blog posts, {len(howto_items)} howto guides & {len(programe_items)} programs compiled.")


if __name__ == "__main__":
    main()
