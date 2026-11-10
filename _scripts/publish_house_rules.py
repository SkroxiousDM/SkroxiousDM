from pathlib import Path
from urllib.parse import unquote, urlsplit, quote
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/7. House Rules'
OUTPUT = ROOT / 'house-rules'
BASE = '/SkroxiousDM'
files = sorted((p for p in SOURCE.rglob('*') if p.is_file() and p.suffix.lower() in ('.md', '.markdown')), key=lambda p: p.relative_to(SOURCE).as_posix().casefold())
if not files:
    raise SystemExit('No house-rule Markdown files found')

def slug(value):
    result = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    if not result:
        raise ValueError('Empty slug: ' + value)
    return result

routes = {}
names = {}
used = set()
for path in files:
    relative = path.relative_to(SOURCE).with_suffix('')
    route = '/house-rules/' + '/'.join(slug(part) for part in relative.parts) + '/'
    if route in used:
        raise ValueError('Duplicate house-rule route: ' + route)
    used.add(route)
    routes[path.resolve()] = route
    names.setdefault(path.stem.casefold(), []).append(path.resolve())

def title(path):
    return re.sub(r'[_-]+', ' ', path.stem)

def page(title_text, route, body):
    return ('---\nlayout: default\ntitle: ' + json.dumps(title_text, ensure_ascii=False) + '\npermalink: ' + route + '\n---\n' + body)

def target_url(target, current):
    target = target.strip()
    parsed = urlsplit(target)
    if not target or target.startswith('#') or parsed.scheme not in ('', 'https', 'http'):
        return target
    if parsed.netloc and parsed.netloc.lower() != 'skroxiousdm.github.io':
        return target
    decoded = unquote(parsed.path)
    candidates = []
    if decoded.startswith(BASE + '/'):
        decoded = decoded[len(BASE) + 1:]
        candidates.append(ROOT / decoded)
        if decoded.startswith('7. House Rules/'):
            candidates.append(ROOT / 'docs' / decoded)
    else:
        candidates.extend([current.parent / decoded, SOURCE / decoded])
    expanded = []
    for candidate in candidates:
        expanded.append(candidate.resolve())
        if not candidate.suffix:
            expanded.extend(candidate.with_suffix(ext).resolve() for ext in ('.md', '.markdown'))
    matches = [candidate for candidate in expanded if candidate in routes]
    if not matches:
        by_name = names.get(Path(decoded).stem.casefold(), [])
        if len(by_name) == 1:
            matches = by_name
    fragment = ('#' + parsed.fragment) if parsed.fragment else ''
    if matches:
        return BASE + routes[matches[0]] + fragment
    for candidate in expanded:
        if candidate.is_file() and candidate.suffix.lower() not in ('.md', '.markdown') and candidate.is_relative_to(SOURCE):
            relative = candidate.relative_to(SOURCE)
            destination = ROOT / 'assets/house-rules' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, destination)
            return BASE + '/assets/house-rules/' + quote(relative.as_posix(), safe='/') + fragment
    for candidate in expanded:
        if candidate.is_file() and candidate.is_relative_to(ROOT):
            relative = quote(candidate.relative_to(ROOT).as_posix(), safe='/')
            return 'https://github.com/SkroxiousDM/SkroxiousDM/blob/main/' + relative + fragment
    if not parsed.netloc:
        print('Unresolved link:', current.relative_to(SOURCE), target)
    return target

def convert(text, current):
    def markdown_link(match):
        return match[1] + target_url(match[2], current) + match[3]
    def wiki_link(match):
        value = match[2]
        target, separator, label = value.partition('|')
        resolved = target_url(target, current)
        if resolved == target:
            return match[0]
        return ('!' if match[1] else '') + '[' + (label if separator else Path(target.split('#')[0]).stem) + '](' + resolved + ')'
    result = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            character = marker[1][0]
            if fence is None:
                fence = character
            elif fence == character:
                fence = None
            result.append(line)
            continue
        if fence is None:
            line = re.sub(r'(!?)\[\[([^\]]+)\]\]', wiki_link, line)
            line = re.sub(r'(!?\[[^\]\n]*\]\()([^\n)]*)(\))', markdown_link, line)
        result.append(line)
    return ''.join(result)

OUTPUT.mkdir(parents=True, exist_ok=True)
index = ['[Back to campaign reference](' + BASE + '/campaign/)\n', '> House-rule reference. Confirm with your GM which rules apply.\n', '## All house rules\n']
for path in files:
    route = routes[path.resolve()]
    text = path.read_text(encoding='utf-8-sig')
    text = re.sub(r'\A---\r?\n.*?\r?\n---\r?\n', '', text, count=1, flags=re.S)
    if '{% endraw %}' in text:
        raise ValueError('Unsupported Liquid endraw in ' + str(path))
    text = convert(text, path)
    body = ('[House rules index](' + BASE + '/house-rules/) | [Campaign reference](' + BASE + '/campaign/)\n\n{% raw %}\n' + text + '\n{% endraw %}\n')
    destination = ROOT / route.strip('/') / 'index.md'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page(title(path), route, body), encoding='utf-8')
    label = path.relative_to(SOURCE).with_suffix('').as_posix().replace('_', ' ')
    index.append('- [' + label + '](' + BASE + route + ')\n')
(OUTPUT / 'index.md').write_text(page('House Rules', '/house-rules/', '\n'.join(index)), encoding='utf-8')
print('Generated', len(files), 'house-rule pages plus the complete index')
