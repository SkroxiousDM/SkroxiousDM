from pathlib import Path
from urllib.parse import unquote, urlsplit
from html import unescape
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('campaign', '_includes/campaign', 'docs/RoS-CoS-RRL', 'docs/simple-quest', 'docs/Curse-of-Strahd-Reloaded-main')
ARCHIVES = ('RoS-CoS-RRL', 'simple-quest', 'Curse-of-Strahd-Reloaded-main')
ANCHOR = re.compile(r'<a\b(?P<attrs>[^>]*)>.*?</a\s*>', re.I | re.S)
HREF = re.compile(r'\bhref\s*=\s*([\x22\x27])(.*?)\1', re.I | re.S)

def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)

def prepare(root):
    for relative in SOURCES:
        remove(root / relative)

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
    prefixes = ('/campaign',) + tuple('/' + name for name in ARCHIVES) + tuple('/docs/' + name for name in ARCHIVES)
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
    remove(site / 'campaign')
    remove(site / '_includes/campaign')
    for name in ARCHIVES:
        for prefix in ('docs', 'assets/reference/docs', 'assets/house-rules'):
            remove(site / prefix / name)
    for path in site.rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        updated = clean_html(text, base, site_url)
        if updated != text:
            path.write_text(updated, encoding='utf-8')
    if (site / 'campaign').exists():
        raise RuntimeError('Campaign output remains in the deployment artifact')
    print('Campaign pages and their site navigation excluded from deployment')

if __name__ == '__main__':
    if sys.argv[1:] == ['prepare']:
        prepare(ROOT)
    elif sys.argv[1:] == ['prune']:
        from site_links import read_site_config
        site_url, base = read_site_config(ROOT / '_config.yml')
        prune(ROOT, base, site_url)
    else:
        raise SystemExit('Usage: unpublish_campaign.py prepare|prune')
