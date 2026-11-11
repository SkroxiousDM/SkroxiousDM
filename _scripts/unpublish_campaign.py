from pathlib import Path
from urllib.parse import unquote, urlsplit
from html import unescape
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('campaign', '_includes/campaign', 'docs/Curse-of-Strahd-Reloaded-main')
ARCHIVES = ('Curse-of-Strahd-Reloaded-main',)
NOTE_ROUTES = ('places-and-persons', 'player-hooks', 'treasure', 'strahd-answers', 'exethanter', 'creepy-mirror', 'dining-hall')
ANCHOR = re.compile(r'<a\b(?P<attrs>[^>]*)>.*?</a\s*>', re.I | re.S)
HREF = re.compile(r'\bhref\s*=\s*([\x22\x27])(.*?)\1', re.I | re.S)
LANDING = """---
layout: default
title: Campaign Library
permalink: /campaign/
---
> Campaign material may contain spoilers. Consult your GM before browsing.

- [Characters and recaps]({{ '/campaign/chronicle/' | relative_url }})
- [Quests, journals, and lore]({{ '/campaign/quests-and-lore/' | relative_url }})
- [Reference library]({{ '/reference/' | relative_url }})

The separate repository campaign notes are not published here.
"""

def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)

def prepare(root):
    # Only the temporary build checkout is changed; GitHub sources are retained.
    for relative in SOURCES:
        remove(root / relative)
    landing = root / 'campaign/index.md'
    landing.parent.mkdir(parents=True, exist_ok=True)
    landing.write_text(LANDING, encoding='utf-8')

def hidden_link(target, base, site_url):
    parsed = urlsplit(unescape(target))
    hosts = {'skroxiousdm.github.io', 'skroxiousdm.com', 'www.skroxiousdm.com', urlsplit(site_url).netloc.casefold()}
    if parsed.netloc and parsed.netloc.casefold() not in hosts:
        return False
    path = unquote(parsed.path)
    if path.startswith('/SkroxiousDM/'):
        path = path[len('/SkroxiousDM'):]
    elif base and path.startswith(base + '/'):
        path = path[len(base):]
    path = '/' + path.lstrip('/')
    prefixes = tuple('/campaign/' + name for name in NOTE_ROUTES) + tuple('/' + name for name in ARCHIVES) + tuple('/docs/' + name for name in ARCHIVES)
    return any(path == prefix or path.startswith(prefix + '/') for prefix in prefixes)

def clean_html(text, base, site_url):
    def anchor(match):
        href = HREF.search(match['attrs'])
        return '' if href and hidden_link(href[2], base, site_url) else match[0]
    return ANCHOR.sub(anchor, text)

def prune(root, base, site_url):
    site = root / '_site'
    if not site.is_dir():
        raise RuntimeError('Missing Jekyll output directory')
    for name in NOTE_ROUTES:
        remove(site / 'campaign' / name)
    remove(site / '_includes/campaign')
    for name in ARCHIVES:
        for prefix in ('docs', 'assets/reference/docs', 'assets/house-rules'):
            remove(site / prefix / name)
    for path in site.rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        updated = clean_html(text, base, site_url)
        if updated != text:
            path.write_text(updated, encoding='utf-8')
    if any((site / 'campaign' / name).exists() for name in NOTE_ROUTES):
        raise RuntimeError('Unpublished repository campaign notes remain in the artifact')
    print('Repository campaign notes excluded; docs-backed campaign libraries retained')

if __name__ == '__main__':
    if sys.argv[1:] == ['prepare']:
        prepare(ROOT)
    elif sys.argv[1:] == ['prune']:
        from site_links import read_site_config
        site_url, base = read_site_config(ROOT / '_config.yml')
        prune(ROOT, base, site_url)
    else:
        raise SystemExit('Usage: unpublish_campaign.py prepare|prune')
